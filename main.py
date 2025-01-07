from models.geo_agent import GeoAgent

def main():
    agent = GeoAgent()
    
    print("Ask a question about a specific location (or 'quit' to exit):")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                break
                
            result = agent.process_input(user_input)
            print("Answer:", result)
            print("\nAsk another question (or 'quit' to exit):")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("\nPlease try again:")
            continue

if __name__ == "__main__":
    main()


