#!/usr/bin/env

import boto3
import os
import sys
import json
from collections import OrderedDict

MAX_ITEMS = 10

class IAMDumpService:
	def __init__(self):
		self._client = boto3.client('iam')

	def _get_all(self, method, content_tag):
		marker = None
		out = []
		while True:
			query = {'MaxItems': MAX_ITEMS}
			if marker is not None:
				query['Marker'] = marker
			res = method(**query)
			out.extend(res[content_tag])
			if res['IsTruncated']:
				print "Results is truncated: %d items fetched" % len(out)
				marker = res['Marker']
			else:
				break
		return out
		
	def sync(self, target):
		users = sorted([self.__parse_user(user) for user in self._get_all(self._client.list_users, 'Users')], \
			key=lambda user: user['CreateDate'], reverse=True)
		with open("%s/users.json" % target, "w") as out:
			json.dump(users, out, indent=4)

		groups = sorted([self.__parse_group(group) for group in self._get_all(self._client.list_groups, 'Groups')], \
			key=lambda user: user['CreateDate'], reverse=True)
		with open("%s/groups.json" % target, "w") as out:
			json.dump(groups, out, indent=4)

	@staticmethod
	def __parse_user(user):
		return OrderedDict({
			'UserName': user['UserName'],
			'Arn': user['Arn'],
			'CreateDate': user['CreateDate'].strftime("%Y-%m-%d %H-%M-%S")
		})

	@staticmethod
	def __parse_group(group):
		return OrderedDict({
			'GroupName': group['GroupName'],
			'Arn': group['Arn'],
			'CreateDate': group['CreateDate'].strftime("%Y-%m-%d %H-%M-%S")
		})

if __name__ == "__main__":
	dump = IAMDumpService()
	dump.sync(sys.argv[1])
	
