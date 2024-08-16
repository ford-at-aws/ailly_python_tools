import importlib
from audit_gen import main as audit_gen
from audit_genv2 import main as audit_genv2
from audit_parse import main as audit_parse
from audit_clean import main as audit_clean
from audit_snippets import main as audit_snippets  # Import the main function from audit_listsnippets

def main():
    choice = input("1: review\n2: refactor\n3: parse\n4: clean\n5: list snippets\n").strip()

    if choice == '1':
        audit_gen()
    elif choice == '2':
        audit_genv2()
    elif choice == '3':
        audit_parse()
    elif choice == '4':
        audit_clean()
    elif choice == '5':
        audit_snippets()
    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
        return

if __name__ == "__main__":
    main()

