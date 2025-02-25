from flask import Flask, render_template, request

app = Flask(__name__)

# Pricing parameters for each car type
pricing_params = {
    "Car Plus": {"body_fare_base": 1500, "fare_per_kilo": 12, "mileage_for_Gas": 14, "mileage_for_Oil": 9, "Oil_Price": 130, "Gas_Price": 43, "driver_stay_fee": 500, "reducer_discount_districts_body": 0.25},
    "Car Prime": {"body_fare_base": 2000, "fare_per_kilo": 12, "mileage_for_Gas": 12, "mileage_for_Oil": 9, "Oil_Price": 130, "Gas_Price": 43, "driver_stay_fee": 600, "reducer_discount_districts_body": 0.25},
    "Car Max": {"body_fare_base": 2500, "fare_per_kilo": 15, "mileage_for_Gas": 10, "mileage_for_Oil": 7.5, "Oil_Price": 130, "Gas_Price": 43, "driver_stay_fee": 700, "reducer_discount_districts_body": 0.25}
}

# Helper function to calculate fuel cost
def cost_Calculation(estimated_destination_distance, mileage_type, fuel_price):
    mileage = estimated_destination_distance / mileage_type
    cost = mileage * fuel_price
    return cost

# Helper function to calculate fuel cost based on fuel type
def calculate_fuel_cost(distance, fuel_type, mileage_gas, mileage_oil, Gas_Price, Oil_Price):
    if fuel_type == 'Gas':
        return cost_Calculation(distance, mileage_gas, Gas_Price)
    else:
        return cost_Calculation(distance, mileage_oil, Oil_Price)

# Calculate price for one-way trip
def calculate_price_OneWay(params):
    body_fare_base = params['body_fare_base']
    estimated_destination_distance = params['estimated_destination_distance']
    mileage_oil = params['mileage_for_Oil']
    mileage_gas = params['mileage_for_Gas']
    Oil_Price = params['Oil_Price']
    Gas_Price = params['Gas_Price']
    Lower_PSRM_Peripheria = params['Lower_PSRM_Peripheria']
    toll_fee = params['toll_fee']
    dropoff_fuel_type = params['dropoff_gas_oil_mapping']
    return_fuel_type = params['return_gas_oil_mapping']
    dropoff_surge = params['dropoff_surge']
    reducer_discount_districts_body = params['reducer_discount_districts_body']

    # Apply discount if surge is 'Yes'
    if dropoff_surge == 'Yes':
        body_fare_base *= reducer_discount_districts_body

    # Calculate fuel cost for dropoff and return
    cost = calculate_fuel_cost(estimated_destination_distance, dropoff_fuel_type, mileage_gas, mileage_oil, Gas_Price, Oil_Price)
    return_cost = calculate_fuel_cost(Lower_PSRM_Peripheria, return_fuel_type, mileage_gas, mileage_oil, Gas_Price, Oil_Price)

    # Calculate total price
    total_toll_fee = toll_fee * 2
    total_price = body_fare_base + cost + return_cost + total_toll_fee + 250  # 250 is safety coverage + booking fee

    return total_price

# Calculate price for round trip
def calculate_price_roundTrip(params):
    body_fare_base = params['body_fare_base']
    n_days = params['n_days']
    estimated_destination_distance = params['estimated_destination_distance']
    mileage_oil = params['mileage_for_Oil']
    mileage_gas = params['mileage_for_Gas']
    Oil_Price = params['Oil_Price']
    Gas_Price = params['Gas_Price']
    estimated_return_distance = params['estimated_return_distance']
    toll_fee = params['toll_fee']
    driver_stay_fee = params['driver_stay_fee']
    dropoff_fuel_type = params['dropoff_gas_oil_mapping']
    return_fuel_type = params['return_gas_oil_mapping']

    # Calculate fuel cost for dropoff and return
    cost = calculate_fuel_cost(estimated_destination_distance, dropoff_fuel_type, mileage_gas, mileage_oil, Gas_Price, Oil_Price)
    return_cost = calculate_fuel_cost(estimated_return_distance, return_fuel_type, mileage_gas, mileage_oil, Gas_Price, Oil_Price)

    # Calculate body fare based on number of days
    if n_days == 1:
        body_fare = body_fare_base
    elif n_days == 2:  # 2 days, 1 night
        body_fare = body_fare_base * n_days
    elif n_days == 3:  # 3 days, 2 nights
        body_fare = (body_fare_base * n_days) * 0.85
    elif n_days == 4:  # 4 days, 3 nights
        body_fare = (body_fare_base * n_days) * 0.80
    elif n_days == 5:  # 5 days, 4 nights
        body_fare = (body_fare_base * n_days) * 0.78
    else:  # More than 5 days
        body_fare = (body_fare_base * n_days) * 0.7

    # Calculate driver stay fee
    stay_fee = driver_stay_fee if n_days == 1 else driver_stay_fee * (n_days - 1)

    # Calculate total price
    total_toll_fee = toll_fee * 2
    total_price = body_fare + cost + return_cost + total_toll_fee + stay_fee + 250  # 250 is safety coverage + booking fee

    return total_price

# Flask route to handle form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        car_type = request.form.get('car_type')  # Selection option: Car Plus, Car Prime, Car Max
        trip_type = request.form.get('trip_type')  # Radio button: One-way Trip, Round Trip
        distance = float(request.form.get('distance'))  # Text field: User input as number
        dropoff_fuel_type = request.form.get('dropoff_fuel_type')  # Radio button: Gas, Oil
        return_fuel_type = request.form.get('return_fuel_type')  # Radio button: Gas, Oil
        toll_fee = float(request.form.get('toll_fee'))  # Text field: User input as number
        n_days = max(int(request.form.get('n_days', 1)), 1)  # Text field: User input as int number (minimum 1)
        dropoff_surge = request.form.get('dropoff_surge', 'No')  # Radio button: Yes, No

        # Validate inputs
        if distance < 0:
            return render_template('index.html', error="Distance cannot be negative.")
        if dropoff_fuel_type not in ['Gas', 'Oil'] or return_fuel_type not in ['Gas', 'Oil']:
            return render_template('index.html', error="Invalid fuel type selected.")

        # Prepare params dictionary
        params = {
            'body_fare_base': pricing_params[car_type]['body_fare_base'],
            'fare_per_kilo': pricing_params[car_type]['fare_per_kilo'],
            'mileage_for_Gas': pricing_params[car_type]['mileage_for_Gas'],
            'mileage_for_Oil': pricing_params[car_type]['mileage_for_Oil'],
            'Gas_Price': pricing_params[car_type]['Gas_Price'],
            'Oil_Price': pricing_params[car_type]['Oil_Price'],
            'driver_stay_fee': pricing_params[car_type]['driver_stay_fee'],
            'toll_fee': toll_fee,
            'estimated_destination_distance': distance,
            'estimated_return_distance': distance,
            'n_days': n_days,
            'Lower_PSRM_Peripheria': distance - 15,
            'dropoff_gas_oil_mapping': dropoff_fuel_type,
            'return_gas_oil_mapping': return_fuel_type,
            'dropoff_surge': dropoff_surge,
            'reducer_discount_districts_body': pricing_params[car_type]['reducer_discount_districts_body']
        }

        # Calculate price
        if trip_type == "One-way Trip":
            price = calculate_price_OneWay(params)
        else:
            price = calculate_price_roundTrip(params)

        return render_template('index.html', price=price)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)