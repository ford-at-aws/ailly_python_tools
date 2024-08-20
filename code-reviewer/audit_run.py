from audit_genv1 import main as audit_gen
from audit_genv2 import main as audit_genv2
from audit_parse import main as audit_parse
from audit_clean import main as audit_clean

def main():
    choice = input("1: review\n2: refactor\n3: parse\n4: clean\n").strip()

    if choice == '1':
        audit_gen()
    elif choice == '2':
        audit_genv2()
    elif choice == '3':
        audit_parse()
    elif choice == '4':
        audit_clean()
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
        return

if __name__ == "__main__":
    main()

