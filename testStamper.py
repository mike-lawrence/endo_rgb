if __name__ == '__main__':

	stamperWindowSize = (200,200)
	stamperWindowPosition = (0,0)
	stamperWindowColor = [255,255,255]
	stamperDoBorder = True

	responseModality = 'trigger' # 'key' or 'trigger'
	triggerLeftAxis = 2
	triggerRightAxis = 5
	triggerCriterionValue = -(2**16/4) #16 bit precision on the triggers, split criterion @a 25%
	horizontalAxisLeft = 0
	verticalAxisLeft = 1
	horizontalAxisRight = 3
	verticalAxisRight = 4

	import fileForker


	stamperChild = fileForker.childClass(childFile='stamperChild.py')
	stamperChild.initDict['windowSize'] = stamperWindowSize
	stamperChild.initDict['windowPosition'] = stamperWindowPosition
	stamperChild.initDict['windowColor'] = stamperWindowColor
	stamperChild.initDict['doBorder'] = stamperDoBorder
	stamperChild.start()
	done = False
	while not done:
		if not stamperChild.qFrom.empty():
			event = stamperChild.qFrom.get()
			if event['type']=='key':
				response = event['value']
				if response=='escape':
					done = True
			elif event['type'] == 'axis':
				if event['axis']==horizontalAxisLeft:
					if (event['value']>((2**16)/3)) or (event['value']<(-(2**16)/3)):
						print event
	stamperChild.stop(killAfter=60)
