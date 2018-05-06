import json
from subprocess import Popen, PIPE
import operator
import time
from pprint import pprint

MASTERS_ID = [
	860449985518862336, 
]

MIN_INTERSECT = 3

FOLLOW_IDS = {}

def follow(tid):
	URI = "/1.1/friendships/create.json?user_id={i}&follow=true"
	while True:
		p = Popen(['twurl', URI.format(i=tid), "-t", "-X", "POST"], stdin=PIPE, stderr=PIPE, stdout=PIPE)
		print("Trying to follow user {u} ...".format(u=tid))
		o,e = p.communicate()
		if "Rate limit exceeded" not in o:
			print("All good !")
			break
		else:
			i = e.index("x-rate-limit-reset: ")
			ee = e[i+len("x-rate-limit-reset: "):]
			i = ee.index("\n")
			eee = ee[:i-5]
			waiting = 1 + int(eee) - time.time()
			print("Waiting {m}:{s} ...".format(m=int(waiting)/60, s=int(waiting)%60))
			time.sleep(waiting)


def get_following(tid):
	URI = "/1.1/friends/ids.json?user_id="
	while True:
		o,e = Popen(['twurl', URI+str(tid), "-t"], stdin=PIPE, stderr=PIPE, stdout=PIPE).communicate()
		print("Trying to get followings for user {u} ...".format(u=tid))
		if "Rate limit exceeded" not in o:
			j = json.loads(o)
			print("All good ! {c} contacts retrieved ...".format(c=len(j['ids'])))
			return j['ids']
		else:
			i = e.index("x-rate-limit-reset: ")
			ee = e[i+len("x-rate-limit-reset: "):]
			i = ee.index("\n")
			eee = ee[:i-5]
			waiting = 1 + int(eee) - time.time()
			print("Waiting {m}:{s} ...".format(m=int(waiting)/60, s=int(waiting)%60))
			time.sleep(waiting)

for MASTER_ID in MASTERS_ID:
	ids = get_following(MASTER_ID)
	for id in ids:
		if id in FOLLOW_IDS:
			FOLLOW_IDS[id] += 1
		else:
			FOLLOW_IDS[id] = 1

FOLLOW_IDS = sorted(FOLLOW_IDS.items(), key=operator.itemgetter(1), reverse=True)

for ID, N in FOLLOW_IDS:
	if N >= MIN_INTERSECT and ID not in MASTERS_ID:
		follow(ID)

for ID in MASTERS_ID:
	follow(ID)
