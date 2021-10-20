from math import ceil, floor
import re

# Constants
colNum = 5
categorizeLowerBound = 2

class Subject:
	# Static variables
	# Dictionary of all subjects. Key: subjectName, Val: subject object
	subjects = {}

	def __init__(self, subjectName):
		# Name of the subject
		self.name = subjectName
		# Array of classes the subject have
		self.__subClasses = []

	def __addClass(self, classNumber):
		c = Class(classNumber)
		self.__subClasses = self.__subClasses + [c]
		return c

	def __moveClass(self, c):
		self.__subClasses = self.__subClasses + [c]

	def getSubClasses(self):
		return self.__subClasses

	@staticmethod
	def __add(className):
		ref = re.search("[a-zA-Z]+", className)
		subjectName = ref.group(0).upper()
		ref = re.search("[0-9&]+", className)
		classNumber = ref.group(0)
		assert subjectName != "" and classNumber != "" and subjectName != "OTHER", "Wrong class name"
		if subjectName not in Subject.subjects:
			s = Subject(subjectName)
			Subject.subjects[subjectName] = s
			c = s.__addClass(classNumber)
		else:
			c = Subject.subjects[subjectName].__addClass(classNumber)
		return c
	
	@staticmethod
	def processClassData():
		f = open("courseDetails.bin", "r")
		subjectLinkList = f.read().strip().split("\n\n")
		for item in subjectLinkList:
			subjectLink = item.strip().split("\n")
			c = Subject.__add(subjectLink[0].strip())
			for i in range(1, len(subjectLink)):
				temp = subjectLink[i].split(",")
				description = temp[0].strip()
				link = temp[1].strip()
				c.addLink(description, link)
		s = Subject("OTHER")
		subjectList = list(Subject.subjects.values())
		toRemove = set()
		for i in range(len(subjectList)):
			subject : Subject = subjectList[i]
			subClasses = subject.getSubClasses()
			if len(subClasses) <= categorizeLowerBound:
				item : Class
				for item in subClasses:
					item.setAlternativeName(subject.name)
					s.__moveClass(item)
					toRemove.add(subject.name)
		for remove in toRemove:
			Subject.subjects.pop(remove)
		Subject.subjects["OTHER"] = s

	@staticmethod
	def getTopMenu():
		subjects = sorted(Subject.subjects.keys())
		res = ""
		for subject in subjects:
			res += """\t\t<button onclick='goToAndHighlight("{0}");'>{0}</button><br>\n"""\
					.format(subject)
		return res[:-1]

	@staticmethod
	def getDetails():
		subjects = sorted(Subject.subjects.keys())
		res = ""
		for name in subjects:
			res += """\t\t<div id="{}" style="height: 100%; width: 100%; display: flex; flex-wrap: wrap; user-select: none;">\n"""\
					.format(name)
			subClasses = Subject.subjects[name].getSubClasses()
			subClasses = sorted(subClasses, key=lambda item : item.getClassNumber())
			length = len(subClasses)
			rowNum = ceil(length / colNum)
			for i in range(rowNum):
				start = i * colNum
				end = min((i + 1) * colNum, length)
				res += """\t\t\t<div id="row" style="width: 100%; display: flex;">\n"""
				for j in range(start, end):
					currentClass : Class = subClasses[j]
					links = currentClass.getSortedLinks()
					if (currentClass.getAlternativeName() == ""):
						preferredName = name
					else:
						preferredName = currentClass.getAlternativeName()
					res += """\t\t\t\t<div id="column" style="width: {}%">\n\t\t\t\t\t<b>{} {}</b><br>\n"""\
							.format(floor(100 / colNum), preferredName, currentClass.getClassNumber())
					res += """\t\t\t\t\t<div id="linksContainer">\n"""
					for k in range(len(links)):
						res += """\t\t\t\t\t\t<a href="{}">{}</a><br>\n"""\
								.format(links[k][1], links[k][0])
					res += """\t\t\t\t\t</div>\n\t\t\t\t</div>\n"""
				res += """\t\t\t</div><div style="width:100%; height: 10px"></div>\n"""
			res += """\t\t</div><hr>\n\n"""

		return res[:-2]


class Class:
	def __init__(self, classNumber):
		# Class number
		self.__number = classNumber
		# All urls that a class have
		self.__urls = {}
		# Alternative name used in OTHER category
		self.__alternativeName = ""
	
	def addLink(self, description, link):
		assert description not in self.__urls, "Class link duplication"
		self.__urls[description] = link
	
	def getClassNumber(self):
		return self.__number

	def getSortedLinks(self):
		return sorted(self.__urls.items(), key=lambda item : item[0].lower())

	def setAlternativeName(self, name):
		self.__alternativeName = name

	def getAlternativeName(self):
		return self.__alternativeName

class QuickLink:
	# Static variables
	# All urls that quick link have
	urls = {}
		
	@staticmethod
	def getQuickLink():
		f = open("quickLinks.bin", "r")
		linkList = f.read().strip().split("\n")
		for item in linkList:
			temp = item.split(",")
			description = temp[0].strip()
			link = temp[1].strip()
			assert description not in QuickLink.urls, "Quicklink duplication"
			QuickLink.urls[description] = link
		res = ""
		sortedList = sorted(QuickLink.urls.items(), key=lambda item : item[0].lower())
		length = len(sortedList)
		rowNum = ceil(length / colNum)
		for i in range(colNum):
			start = i * rowNum
			end = min((i + 1) * rowNum, length)
			res += """\t\t\t<div id="column" style="width: {}%; user-select: none;">\n\t\t\t\t<b>{}-{}</b><br>\n"""\
					.format(floor(100 / colNum), sortedList[start][0][0], sortedList[end - 1][0][0])
			res += """\t\t\t\t<div id="linksContainer">\n"""
			for j in range(start, end):
				res += """\t\t\t\t\t<a href="{}">{}</a><br>\n"""\
						.format(sortedList[j][1], sortedList[j][0])
			res += """\t\t\t\t</div>\n\t\t\t</div>\n\n"""
		return res[:-2]
	



Subject.processClassData()
f = open("template.html", "r")
strRead = f.read().split("<!-- DIV -->")
strRes = ""
# Top menu
strRes += strRead[0]
strRes += Subject.getTopMenu()
strRes += strRead[1]
strRes += QuickLink.getQuickLink()
strRes += strRead[2]
strRes += Subject.getDetails()
strRes += strRead[3]

f = open("index.html", "w")
f.write(strRes)


