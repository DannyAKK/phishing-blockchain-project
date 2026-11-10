from assessment import prepare_assessment


def main():
    print("Phishing Assessment Prototype")
    try:
        supplied_input = input("Enter a URL or domain: ")
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled. Exiting.")
        return

    try:
        assessment = prepare_assessment(supplied_input)
    except ValueError as error:
        print(error)
        return

    print("\nInput accepted.")
    print(f"Input type: {assessment.input_type}")
    print(f"Hostname: {assessment.hostname}")
    print("\nThis confirms supported syntax only.")
    print("Phishing assessment is not implemented yet.")


if __name__ == "__main__":
    main()
