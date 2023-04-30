import sys
import multiprocessing
import src.config as config
import src.build as build

def main():
	print(sys.argv)
	if sys.argv[1] == "init":
		config.init_config()
	elif sys.argv[1] == "build":
		if len(sys.argv) > 3:
			if sys.argv[3] == "-dark":
				build.main(sys.argv[2], True)
			else:
				build.main(sys.argv[2], False)
		else:
			build.main(sys.argv[2])

# prevent from running twice
if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()		
