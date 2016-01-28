

#CST:xzahra22

#######################################################
#	file:	cst.py
#	author:	Jiri Zahradnik <xzahra22@stud.fit.vutbr.cz>
#	date:	april 2015
#	note:	I have changed my coding style a littlebit
#			after PhD. Krivka told me, that my code is
#			almost unreadable
#
#	another note: 	I am sorry for so many cycles,
#					however, I do not know any better
#					solution
#
#	
#
# 	Soldier! Do you find something funny about the name
#	....Biggus....Dickus? - The Life of Brian
#######################################################


#######################################################
# import libraries
import os
import re
import sys
import getopt
import codecs
#######################################################


######################################################
# define exit codes
E_OK 			= 0
E_BADARG		= 1
E_WRITEFAIL		= 3
E_READFAIL		= 21
######################################################


#######################################################
# this class specifies unicode escape sequences used in 
# outputs
class bcolors: 
    HEADER 		= '\033[95m'
    OKBLUE 		= '\033[94m'
    OKGREEN 	= '\033[92m'
    WARNING 	= '\033[93m'
    FAIL 		= '\033[91m'
    END 		= '\033[0m'
    BOLD 		= '\033[1m'
    UNDERLINE 	= '\033[4m'
######################################################




#######################################################
# definition of class parser
# constructor of this class is last, because everything
# is being done in him
class parser:
	#######################################################
	# definition of ISO C99 keywords
	keywords = ["auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern", "float",
				"for", "goto", "if", "inline", "int", "long", "register", "restrict", "return", "short", "signed", "sizeof",
				"static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while", "_Bool", "_Complex",
				"_Imaginary"
				]
	######################################################

	help 			= False
	isDirectory		= False
	inputFile		= ""
	arrFiles		= []
	outputFile		= ""
	flag			= ""
	pattern			= ""
	noPath			= False
	noSubDir 		= False
	totalCount		= 0
	arrFileCount	= []
	arrOutputString	= []
	
	###################################################
	# error function to print message and exit with 
	# exit code
	def error(self, message, exitCode):
		if(E_OK != exitCode and "" != message):
			sys.stderr.write(bcolors.BOLD + "ERROR:" + bcolors.END + message + "\n")
		sys.exit(exitCode)
	# end of error
	###################################################


	###################################################
	# help
	def help(self):
		print (
		bcolors.BOLD + "\n\tNOBODY EXPECTS THE SPANNISH INQUISITION" + bcolors.END +
		"\n\tScript counts statistics of .c and .h files in set directory and subdirectories.\n\n"\
		+ bcolors.BOLD +"run syntax:"
		+ bcolors.END +"\tpython3 cst.py [args]\n"\
		+ bcolors.BOLD + "arguments:"\
		+ bcolors.END + "\tone of arguments '-k''-o''-i''-w''-c' is required\n\t\tand unless '--help'"\
		"is set, exactly" + bcolors.BOLD + " one" + bcolors.END + " of these params is required\n\n"\
		"\t\t--input=<file|dir>\tspecifies input file or directory\n\n"\
		"\t\t--nosubdir\t\tsearch will ignore subdirectories\n\n"\
		"\t\t--output=<filename>\tprints outut to specified file\n\n"\
		"\t\t-k\t\t\tprints number of key words for every analyzed file\n\t\t\t\t\tand total count in all files\n\n"
		"\t\t-o\t\t\tprints count of simple operators for each file\n\t\t\t\t\tand total count in all files\n\n"\
		"\t\t-i\t\t\tprints count of identifikators in each file\n\t\t\t\t\tand total count in all files\n\n"\
		"\t\t-w=<pattern>\t\tfinds exact string defined by pattern\n\t\t\t\t\tand prints out count of appearances"\
		"\n\t\t\t\t\tin each file and total\n"\
		"\t\t-c\t\t\tprints total count of comment characters including // /* */ and end of lines\n\n"\
		"\t\t-p\t\t\tprints only names of analyzed files, not full paths"\
		)
	# end of help
	###################################################


	###################################################
	# argument check
	def argCheck(self):
		###############################################
		# get argument count for faster evaluation
		self.argc = len(sys.argv)		
		###############################################


		###############################################
		# find argument help, if any other arg is
		# specified, error
		for isHelp in sys.argv[1:]:
			if("--help" == isHelp and 2 == self.argc):
				self.help();
				#######################################
				# exit with exit code 0
				self.error("", E_OK)

			elif("--help" == isHelp and 2 != self.argc):
				self.error("Parameter '--help' must be used alone", E_BADARG)
		# end of help check
		###############################################


		##############################################
		# check for argument --nosubdir
		for arg in sys.argv[1:]:
			if(re.match(r"^--nosubdir", arg)):
				self.noSubDir = True
				sys.argv.remove(arg)
				break
		###############################################
		

		###############################################
		# continue with argcheck
		# check input
		for arg in sys.argv[1:]:
			if(re.match(r"^--input=.*", arg)):
				self.inputFile	= re.compile(r"^--input=(.*)").search(arg).group(1)
				# normalize path and get canonical path
				self.inputFile	= os.path.normpath(self.inputFile)
				self.inputFile	= os.path.realpath(self.inputFile)
				sys.argv.remove(arg)
				break


		# if '--input=<file|dir>' is empty, stdin is set
		if("" == self.inputFile):
			self.inputFile	= os.path.realpath(__file__)
			self.inputFile	= re.sub(__file__, "", self.inputFile)
		# end of check for input file/dir
		###############################################

		
		###############################################	
		# check output
		for arg in sys.argv[1:]:
			if(re.match(r"^--output=.*", arg)):
				self.outputFile	= re.compile(r"^--output=(.*)").search(arg).group(1)
				# normalize path and get canonical path
				self.outputFile	= os.path.normpath(self.outputFile)
				self.outputFile	= os.path.realpath(self.outputFile)
				sys.argv.remove(arg)
				# find if path exists
				helpString				= self.outputFile.rsplit('/',1)
				path					= helpString[0]
				if(os.path.isdir(path)):
					f = open(self.outputFile, "w+")
					f.close()
					break
				else:
					self.error("Cannot access output file.", E_WRITEFAIL)
		###############################################

		# if '--input=<file|dir>' is empty, stdin is set
		if("" == self.outputFile):
			self.outputFile	= sys.stdout
		# end of check for input file/dir
		###############################################

		
		###############################################
		# find -p
		for arg in sys.argv[1:]:
			if("-p" == arg):
				self.noPath	= True
				sys.argv.remove(arg)
				break
		# end of finding -p
		###############################################


		self.argc = len(sys.argv)


		###############################################
		# find mod
		if(2 != self.argc):
			self.error("Either no mod is specified or too many paramaters", E_BADARG)

		# undortunately switch-case does not exist in python,
		# therefore I am forced to use if/else construct
		if("" == self.flag):	
			if("-k" == sys.argv[1]):
				self.flag	= "k"
			elif("-o" == sys.argv[1]):
				self.flag	= "o"
			elif("-i" == sys.argv[1]):
				self.flag	= "i"
			elif("-c" == sys.argv[1]): # done
				self.flag	= "c"
			# -w flag is set by regex match
			elif(re.match(r"^-w=(.*)", str(sys.argv[1]))):
				self.pattern	= re.compile(r"^-w=(.*)").search(sys.argv[1]).group(1)
				self.flag 	= "w"
			else:
				self.error("Bad parameter(s) were entered. For help enter parameter --help", E_BADARG)

		# end of mod search
		###############################################
	# end of argcheck
	###################################################


	###################################################
	# scan directory for subdirs and files
	# method uses recursion for 
	def scanFileOrDir(self, directory):
		###############################################
		# if input string is .c or .h file, return from function
		if(not os.path.isdir(directory) and re.search(r"\.[cChH]$", directory)):
			self.arrFiles.append(directory)
			return
		elif(not os.path.isdir(directory)):
			return
		###############################################
		for member in os.listdir(directory):
			path	= os.path.join(directory, member)
			if(None != re.search(r"\.[cChH]$", member)):
			# when I find file, i add him to the end of array of files
				self.arrFiles.append(path)
			else:
			# member is susbdir, therefore I go in
				if(not self.noSubDir): # if --nosubdir is set, dont go in subdirs
					self.scanFileOrDir(path)
	# end of scanFileOrDir
	###################################################


	###################################################
	# check whether I can read/write to file
	# method takes array of files and mode and check if 
	# file have rights to read/write
	def rights(self, array, mode):
		if(not sys.stdout == self.outputFile):
			if("R" == mode):
				for readable in array:
					if(not os.access(readable, os.R_OK)):#check readability of file
						self.error("insufficient rights to read file:" + readable, E_READFAIL)
			elif("W" == mode):
				if(not os.access(array, os.W_OK)):#check readability of file
					self.error("insufficient rights to write to file:" + array, E_WRITEFAIL)
	# end of rights check
	###################################################


	###################################################
	# count commented char count FSM implementation
	def commentedChars(self, string):
		state = 0
		count = 0
		returnString = ""
		# now go through file char by char
		for char in string:
			if(0 == state and "/" == char):
				state = 1
			elif(1 == state and "/" != char and "*" != char):
				state = 0
			elif(1 == state and "/" == char):
				state = 2
				count += 2
			elif(1 == state and "*" == char):
				state = 3
				count += 2
			elif(2 == state and "\\" == char):
				state = 5
				count += 1
			elif(2 == state and "\n" != char):
				count += 1
			elif(2 == state and "\n" == char):
				state = 0
				count +=1
			elif(3 == state and "*" != char):
				count += 1
			elif(3 == state and "*" == char):
				count += 1
				state = 4
			elif(4 == state and "/" != char):
				state = 3
				count += 1
			elif(4 == state and "/" == char):
				state = 0
				count += 1
			elif(5 == state):
				state = 2
				count += 1

			###########################################
		###############################################
		return count
	# end of commentedChars()
	###################################################


	###################################################
	# strip strings from file
	def stripStrings(self, string):
		helpString		= ""
		returnString	= ""
		state			= 0
		# FSM for stripping strings "asd"
		for char in string:
			# I am entering comment, do not delete strings
			if(0 == state and "/" == char):
				state			= 1
				returnString 	+= char
			# I am in comment, do not delete strings
			elif(1 == state and "*" == char):
				state	=		 2
				returnString 	+= char
			# I am in comment, do not delete strings
			elif(2 == state and "*" != char):
				returnString	+= char
			# I am leaving comment, do not delete strings
			elif(2 == state and "*" == char):
				state			= 3
				returnString 	+= char
			# Definite leave from comment, do not delete strings
			elif(3 == state and "/" == char):
				state			= 0
				returnString 	+= char
			# I am entering line comment
			elif(1 == state and "/" == char):
				state			= 4
				returnString 	+= char
			# False alarm
			elif(1 == state and "/" == char and "*" != char):
				state 			= 0
				returnString 	+= char
			# I am on new line of line comment
			elif(4 == state and "\\" == char):
				state 			= 7
				returnString 	+= char
			# I am still in line comment
			elif(4 == state and "\n" != char):
				returnString 	+= char
			# I am leaving line comment
			elif(4 == state and "\n" == char):
				state			= 0
				returnString 	+= char
			# I am at the beginning of string
			elif(0 == state and "\"" == char):
				state			= 5
			# I am at the beginning of string
			elif(0 == state and "'" == char):
				state			= 6
			# I am in string and I am not leaving
			elif(5 == state and "\"" != char):
				pass
			# I am in string and I am leaving
			elif(5 == state and "\"" == char):
				state 			= 0
			# I am in string
			elif(6 == state and "'" != char):
				pass
			# I am leaving string
			elif(6 == state and "'" == char):
				state 			= 0
			# I am in normal code
			elif(0 == state):
				returnString 	+= char
			elif(7 == state):
				state			= 4
				returnString	+= char

		###############################################
		return returnString
	# end of strip strings
	###################################################


	###################################################
	# strip comments from file
	def stripComments(self, string):
		state = 0
		returnString = ""
		# now go through file char by char
		for char in string:
			# first char /
			if(0 == state and "\"" == char):
				state = 1
				returnString += char
			elif(0 == state and "'" == char):
				state = 2
				returnString += char
			elif(0 == state and "/" == char):
				state = 3
				returnString += char
			elif(0 == state):
				returnString += char
			elif(1 == state and "\"" != char):
				returnString += char
			elif(1 == state and "\"" == char):
				state = 0
				returnString += char
			elif(2 == state and "'" != char):
				returnString += char
			elif(2 == state and "'" == char):
				state = 0
				returnString += char
			elif(3 == state and "/" == char):
				state = 4
				returnString = returnString[:-1]
			elif(3 == state and "*" == char):
				state = 6
				returnString = returnString[:-1]
			elif(3 == state):
				state = 0
				returnString += char
			elif(4 == state and "\\" == char):
				state = 5
			elif(4 == state and "\n" == char):
				state = 0
			elif(5 == state):
				state = 4
			elif(6 == state and "*" == char):
				state = 7
			elif(6 == state and "*" != char):
				pass
			elif(7 == state and "/" == char):
				state = 0
			elif(7 == state and "/" != char):
				state = 6
			###########################################
		return returnString
		###############################################


	###################################################
	# stripMacros
	def stripMacros(self, string):
		state			= 0
		returnString	= ""
		for char in string:
			if(0 == state and "#" == char):
				state	= 1
			elif(0 == state):
				returnString	+= char
			elif(1 == state and "\\" == char):
				state	= 2
			elif(1 == state and "\n" == char):
				state 	= 0
			elif(2 == state and "\n" == char):
				state 	= 1
		###############################################
		return returnString				
	# end stripMacros
	###################################################


	###################################################
	# stripKeyWords()
	def stripKeyWords(self, string):
		for word in self.keywords:
			string = re.sub(r"(\W)" + word + r"(\W)", r"\1\2", string)
	
		return string
	# end of stripKeyWords
	###################################################

	###################################################
	# cut path from files, only when -p is set
	def cutPath(self):
		index	= 0
		for file in self.arrFiles:
			helpString				= file.rsplit('/',1)
			self.arrFiles[index]	= helpString[1]
			index += 1
	# end of cutPath		
	###################################################


	###################################################
	# prints files out
	def printFiles(self, fileToWrite, filesArray, countArray, totalCount): 
		longestFile 	= 0
		totalCount		= str(totalCount)
		longestNumber	= len(totalCount)
		const_display_width	= 145 # in my opinion this is best number for 13" screen with 1366*768 resolution 
		
		for file in filesArray:
			fileLen		= len(file)
			if(fileLen > longestFile):
				longestFile = fileLen			

		if(len("CELKEM:") > longestFile):
			longestFile = len("CELKEM:")

		width = 0
		width = int(longestNumber) + int(longestFile) + 1
		index = 0

		for file in filesArray:
			fileLen		= len(file)
			intString	= str(countArray[index])
			self.arrOutputString.append(file + " " * (width - fileLen - len(intString)) + intString + "\n")
			index 		+= 1
		# sort output
		self.arrOutputString.sort()
		# if no file is to be analyzed, just pass this
		if(self.arrOutputString):
			self.arrOutputString.append("CELKEM:" + " " * (width - len("CELKEM:") - len(str(totalCount))) + str(totalCount) + "\n")
		else:
			self.arrOutputString.append("CELKEM: 0\n")


		if(not sys.stdout == fileToWrite):
			with codecs.open(fileToWrite, "w+", encoding='iso-8859-2') as f:
				for i in range(0, len(self.arrOutputString)):
					f.write(self.arrOutputString[i])
			f.close()
		else:
			for i in range(0, len(self.arrOutputString)):
				print(self.arrOutputString[i][:-1])
	# end of printing
	###################################################


	###################################################
	# call when -c flag is set
	def cFlagSet(self):
		index = 0
		for readFile in self.arrFiles:
			if(os.access(readFile, os.F_OK)):
				with codecs.open(readFile, "rU", encoding='iso-8859-2') as f:
					string = f.read()
					string = self.stripStrings(string)
					count = self.commentedChars(string)
					self.arrFileCount.append(count)
					self.totalCount += count
				f.close()
			else:
				self.error("File does not exist", 21)
	# end of -c flags
	###################################################


	###################################################
	# cal when -w=pattern is set
	def wFlagSet(self):
		self.totalCount	= 0
		countF			= 0
		for i in range(0, len(self.arrFileCount)):
			self.arrFileCount[i]	= 0

		for file in self.arrFiles:
			if(os.access(file, os.F_OK)):
				with codecs.open(file, "rU", encoding='iso-8859-2') as f:
					string 	= f.read()
					countF 	= string.count(self.pattern)
					self.arrFileCount.append(countF)
					self.totalCount += countF
				f.close()
			else:
				self.error("File does not exist", 21)
	###################################################


	###################################################
	# cal when -w=pattern is set
	def kFlagSet(self):
		self.totalCount	= 0
		for i in range(0, len(self.arrFileCount)):
			self.arrFileCount[i]	= 0

		for file in self.arrFiles:
			if(os.access(file, os.F_OK)):
				countF			= 0
				with codecs.open(file, "rU", encoding='iso-8859-2') as f:		
					string 	= f.read()
					string 	= self.stripStrings(string)
					string 	= self.stripComments(string)
					string 	= self.stripMacros(string)
					for word in self.keywords:
						regex 		= r"\W" + word + r"\W"					
						foundArr	= re.findall(regex, string)
						countF 		+= len(foundArr)
					#######################################
					self.arrFileCount.append(countF)
					self.totalCount	+= countF
				f.close()
			else:
				self.error("File does not exist", 21)
		###############################################
	# end of kFlagSet
	###################################################


	###################################################
	# call when -o flag is set
	def oFlagSet(self):
		self.totalCount	= 0
		for i in range(0, len(self.arrFileCount)):
			self.arrFileCount[i]	= 0

		# define single operators:
		#  ++  --  +  -  +=  -=  *  *=  /  /= %  %=  <  <=  >  >=  ==  !=
		#  !  &&  ||  <<  <<=  >>  >>=  ~  &  &=  |  |=  ^  ^=  =  ->  .
		regex = [	
					r"[^\+]\+\+[^\+]", r"[^\-]\-\-[^\-]",
					r"[^\+]\+[^\+=]", r"[^\-]\-[^\-=>]",
					r"\+=", r"\-=", r"(\*+)[^=]", r"\*=",
					r"/[^=]", r"/=", r"%[^=]",
					r"%=", r"[^<]<[^<=]", r"[^<]<=",
					r"[^>\-]>[^>=]", r"[^>]>=",
					r"==", r"!=", r"![^=]", r"&&[^=]",
					r"\|\|[^\|]", r"<<[^=]", r"<<=",
					r">>[^=]", r">>=", r"~", r"[^&]&[^&=]",
					r"&=", r"[^\|]\|[^\|=]",
					r"\|=", r"\^[^=]", r"\^=",
					r"[^\+\-\*/%<>=!&\|\^]=[^=]", r"\->",
					r"[^\.0-9]\.[^\.0-9]"
				]
		for file in self.arrFiles:
			if(os.access(file, os.F_OK)):
				with codecs.open(file, "rU", encoding='iso-8859-2') as f:
					# read file
					string 	= f.read()
					# strip everything, naked ftw
					string 	= self.stripStrings(string)
					string 	= self.stripComments(string)
					string 	= self.stripMacros(string)
					# iterate through regexes
					countF			= 0
					for r in regex:
						help 		= re.findall(r, string)
						for h in help:
							countF 	+= 1
						###################################
					#######################################
					self.arrFileCount.append(countF)
					self.totalCount	+= countF
				###########################################
				f.close()
			else:
				self.error("File does not exist", 21)
		###############################################
	# end of -o flag
	###################################################
			

	###################################################
	# flag -i set
	def iFlagSet(self):
		self.totalCount	= 0
		for i in range(0, len(self.arrFileCount)):
			self.arrFileCount[i]	= 0

		for file in self.arrFiles:
			if(os.access(file, os.F_OK)):
				with codecs.open(file, "rU", encoding='iso-8859-2') as f:
					# read file
					string 	= f.read()
					# strip everything, naked ftw
					string 	= self.stripStrings(string)
					string 	= self.stripComments(string)
					string 	= self.stripMacros(string)
					string 	= self.stripKeyWords(string)
					string = re.findall(r"[a-zA-Z_]+?\w*", string)
					countF = len(string)
					self.arrFileCount.append(countF)
					self.totalCount += countF 
				f.close()
			else:
				self.error("File does not exist", 21)
	# end of iFlagSet
	###################################################


	###################################################
	# constructor of class is last, because everything 
	# happens in this
	def __init__(self):
	# check argumetns
		self.argCheck()
		if(os.path.isdir(self.inputFile)):
			self.scanFileOrDir(self.inputFile)
		elif(os.path.isfile(self.inputFile)):
			self.arrFiles  = [self.inputFile]
		else:
			self.error("Err msg", 2)

			

		###############################################
		# check if I can read from files
		self.rights(self.arrFiles, "R")
		###############################################


		###############################################
		# check if I can write to output
		self.rights(self.outputFile, "W")	
		###############################################
		

		###############################################
		# flag is enabled
		if("c" == self.flag):
			self.cFlagSet()
			
		if("w" == self.flag):
			self.wFlagSet()

		if("k" == self.flag):
			self.kFlagSet()
		
		if("o" == self.flag):
			self.oFlagSet()

		if("i" == self.flag):
			self.iFlagSet()

		
		

		###############################################
		# if -p is set, cut paths
		if(self.noPath):
			self.cutPath()


		###############################################
		# print files
		self.printFiles(self.outputFile, self.arrFiles, self.arrFileCount, self.totalCount)

	# end of constructor
	###################################################

# end of class parser
#######################################################


#######################################################
# main()
x = parser()