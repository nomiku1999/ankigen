import requests

word = "comfort"
# Returns a clean 400x400 photo matching your specific vocabulary word
image_url = f"https://loremflickr.com/400/400/{word}"

print(f"Fetching a placeholder photo for '{word}'...")
response = requests.get(image_url, allow_redirects=True)

if response.status_code == 200:
    # Save the binary photo out to disk
    filename = f"{word}.jpg"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Saved image cleanly to your local folder as: {filename}")
else:
    print("Could not download image.")