import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from odmantic.bson import Int64 as int64
from typing import Optional
from odmantic import Field, Model
from datetime import datetime
import os

mongodb_url = os.environ["mongodb_url"]


class Mongo(object):
    @staticmethod
    def connect():
        return MongoClient(mongodb_url)

    @staticmethod
    async def aioconnect():
        return AsyncIOMotorClient(mongodb_url)

class odm(object):
    @staticmethod
    async def connect():
        return AIOEngine(motor_client=AsyncIOMotorClient(mongodb_url), database="giffany")

class banned(Model):
    guildid: Optional[int64] = None
    userid: Optional[int64] = None

class colourme(Model):
	guildid: Optional[int64] = None
	reqname: Optional[str] = None
	reqid: Optional[int64] = None
	ignorename: Optional[str] = None
	ignoreid: Optional[int64] = None
	name: Optional[str] = None
	rolename: Optional[str] = None
	roleid: Optional[int64] = None

class giveaways(Model):
	giveawaynum: Optional[int64] = None
	guildid: Optional[int64] = None
	authorid: Optional[int64] = None
	endtime: Optional[datetime] = None
	giveawaychannelid: Optional[int64] = None
	giveawaymessageid: Optional[int64] = None
	reqrid:	Optional[str] = None
	winnersnum:	Optional[str] = None
	prize: Optional[str] = None
	starttime: Optional[datetime] = None

class giveme(Model):
	guildid: Optional[int64] = None
	reqname: Optional[str] = None
	reqid: Optional[int64] = None
	ignorename: Optional[str] = None
	ignoreid: Optional[int64] = None
	name: Optional[str] = None
	rolename: Optional[str] = None
	roleid: Optional[int64] = None

class giveyou(Model):
	guildid: Optional[int64] = None
	name: Optional[str] = None
	rolename: Optional[str] = None
	roleid:	Optional[int64] = None

class hasrole(Model):
	guildid: Optional[int64] = None
	command: Optional[str] = None
	role: Optional[int64] = None

class limbo(Model):
	guild_id: Optional[int64] = None
	user_id: Optional[int64] = None
	roles_ids: Optional[str] = None

class logs(Model):
	guild_id: Optional[int64] = None
	channel_id: Optional[int64] = None

class mutes(Model):
	guildid: Optional[int64] = None
	user: Optional[int64] = None
	roles: Optional[str] = None
	starttime: Optional[datetime] = None
	endtime: Optional[datetime] = None

class persistentroles(Model):
	guildid: Optional[int64] = None
	userid: Optional[int64] = None
	roles: Optional[str] = None

class prefixes(Model):
	guildid: Optional[int64] = None
	prefix: Optional[str] = None
	activecogs: Optional[str] = None
	activecommands: Optional[str] = None

class strikes(Model):
	strikeid: Optional[str] = None
	guildid: Optional[int64] = None
	user: Optional[int64] = None
	moderator: Optional[str] = None
	action: Optional[str] = None
	reason: Optional[str] = None
	day: Optional[str] = None

class tag(Model):
	guild_id: Optional[int64] = None
	author_id: Optional[int64] = None
	names: Optional[str] = None
	content: Optional[str] = None

class tempbans(Model):
	guildid: Optional[int64] = None
	user: Optional[int64] = None
	starttime: Optional[datetime] = None
	endtime: Optional[datetime] = None
	banreason: Optional[str] = None

class userfilter(Model):
	guild: Optional[int64] = None
	user: Optional[int64] = None

class welcomer(Model):
	guildid: Optional[int64] = None
	channelid: Optional[int64] = None
	msg: Optional[str] = None
	achannelid: Optional[int64] = None
	amsg: Optional[str] = None
	leavechannelid: Optional[int64] = None
	leavemsg: Optional[str] = None
