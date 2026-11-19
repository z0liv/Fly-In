import sys

def	main():
	map = sys.argv[1]
	try:
		with open(map) as file:
			print(file.read())
	except Exception as error:
		print(error)
	print("Hello world!")

if __name__ == "__main__":
	main()
