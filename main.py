import requests;

def main():
    x = requests.get("https://api.github.com")
    print(x.status_code)

    y = requests.get("https://api.github.com/repos/tensorflow/tensorflow")
    print(y.status_code)

    for x, y in y.json().items():
        print(f"{x}: {y}")

if __name__ == "__main__":
    main()