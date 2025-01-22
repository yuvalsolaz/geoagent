from models.generate_query_agent import GenerateQueryAgent


def main():
    agent = GenerateQueryAgent()

    print("input location coordinates for generating specific location query (or 'quit' to exit):")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                break

            result = agent.process_input(user_input)
            print("Answer:", result)
            print("\nInput another location (or 'quit' to exit):")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("\nPlease try again:")
            continue


if __name__ == "__main__":
    main()


