def sumRow(line):
	vals = line.split(",")
	sum = 0
	for v in vals:
		try:
			sum += int(v)
		except ValueError:
			pass
	return sum
	
def sumCol(file, colLen):
	lines = file.split("\n")
	numLines = len(lines)
	
	vals = []
	for l in lines[1:]:
		vals.extend(l.split(","))
	
	print len(vals), numLines, colLen
	
	zeroes = 0
	# Sum the ith column
	for i in range(0, colLen):
		sum = 0
		for j in range(0, numLines):
			try:
				sum += int(vals[i+j*colLen])
			except ValueError:
				pass
				
		if sum == 0:
			zeroes += 1
	
	return zeroes
	
f = open("HW3_steele_train.csv", "r")
file = f.read()
f.close()
lines = file.split("\n")

print sumRow(lines[1])
print sumCol(file, len(lines[0].split(",")))