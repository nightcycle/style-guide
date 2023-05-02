import sys
import multiprocessing
import src.config as config
import src.build as build

def main():
	print(sys.argv)
	if sys.argv[1] == "init":
		config.init_config()
	elif sys.argv[1] == "build":
		rojo_path = "default.project.json"
		for arg in sys.argv:
			if ".project.json" in arg:
				rojo_path = arg

		if "-dark" in sys.argv:
			build.main(sys.argv[2], True, rojo_path)
		else:
			build.main(sys.argv[2], False, rojo_path)


# prevent from running twice
if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()		
