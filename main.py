from input_validation import parse_input


def main():
    print("Phishing Assessment Prototype")
    try:
        supplied_input = input("Enter a URL or domain: ")
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled. Exiting.")
        return

    try:
        parsed_input = parse_input(supplied_input)
    except ValueError as error:
        print(error)
        return

    print("\nInput accepted.")
    print(f"Input type: {parsed_input['input_type']}")
    print(f"Hostname: {parsed_input['hostname']}")
    print("\nThis confirms supported syntax only.")
    print("Phishing assessment is not implemented yet.")


if __name__ == "__main__":
    main()
