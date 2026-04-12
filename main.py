import sys

if __name__ == "__main__":
    sys.argv = ["manager.py", "runserver"]

    import manager
    manager.main()