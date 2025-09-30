import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime
# 1. Import the 'request' object from flask
from flask import Flask, jsonify, request

app = Flask(__name__)

consumer_key = "ddu7Qin2pXa1GAUOwtrc60qmMsHpiGMdOGFIFe5zX4nbM9Ap"
consumer_secret = "065Vk9E1wC9CIuRSyTF72s7DH7oTO2Au8fGZaIR0CiVN7TpACoklied9axcAGn9p"
url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"


def ress():
    # It's good practice to wrap network requests in a try-except block
    try:
        res = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=10)
        res.raise_for_status()  # Raise an exception for bad status codes
        return res.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        return None


# 2. Change the function signature to accept no arguments
@app.route("/")
def initiate_stk_push():
    accessToken = ress()

    if accessToken:
        # 3. Get parameters from the request's query string
        amount = request.args.get('amt', type=int)
        phone = request.args.get('tel')
        phone = '254' + phone[1:] if phone and phone.startswith('0') else phone

        print(amount)
        print(phone)

        # 4. Add validation to ensure parameters exist
        if amount is None or phone is None:
            return jsonify({'error': 'The "amt" and "tel" query parameters are required.'}), 400

        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        business_short_code = '174379'
        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        callback_url = 'https://mydomain.com/patzh' # Remember to use ngrok for testing this
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        party_a = phone
        account_reference = 'Pay water Bill NAWASSCO-DEMO'
        transaction_desc = 'Thank you and Welcome again, cc NaxWATER'
        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + accessToken
        }

        stk_push_payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': party_a,
            'PartyB': business_short_code,
            'PhoneNumber': party_a,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            response_data = response.json()
            checkout_request_id = response_data['CheckoutRequestID']
            response_code = response_data['ResponseCode']
            if response_code == "0":
                return jsonify({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
            else:
                return jsonify({'error': 'STK push failed.', 'details': response_data})
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Could not get access token.'}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8967)
    
    
