
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ISLEmojiMapper:

    def __init__(self):

        self.dictionary = self._build_isl_dictionary()
        logger.info(f"ISL Emoji Mapper initialized with {len(self.dictionary)} glosses")

    def _build_isl_dictionary(self) -> Dict[str, Dict[str, Any]]:

        return {

            "I": {
                "emoji": "🙋",
                "lottie": "pronoun_i.json",
                "alternatives": ["👤", "☝️"],
                "confidence": 0.95,
                "category": "pronoun",
                "notes": "Point to self at body center"
            },
            "YOU": {
                "emoji": "👉",
                "lottie": "pronoun_you.json",
                "alternatives": ["☝️", "👤"],
                "confidence": 0.95,
                "category": "pronoun",
                "notes": "Point to addressee (established spatial locus)"
            },
            "HE": {
                "emoji": "👨",
                "lottie": "pronoun_he.json",
                "alternatives": ["👦", "🧑"],
                "confidence": 0.90,
                "category": "pronoun",
                "notes": "Point to established locus for male referent"
            },
            "SHE": {
                "emoji": "👩",
                "lottie": "pronoun_she.json",
                "alternatives": ["👧", "🧑"],
                "confidence": 0.90,
                "category": "pronoun",
                "notes": "Point to established locus for female referent"
            },
            "IT": {
                "emoji": "👆",
                "lottie": "pronoun_it.json",
                "alternatives": ["☝️", "👤"],
                "confidence": 0.85,
                "category": "pronoun",
                "notes": "Point to object or established locus"
            },
            "WE": {
                "emoji": "👥",
                "lottie": "pronoun_we.json",
                "alternatives": ["👫", "👬", "👭"],
                "confidence": 0.90,
                "category": "pronoun",
                "notes": "Multiple people including signer"
            },
            "THEY": {
                "emoji": "🗣️",
                "lottie": "pronoun_they.json",
                "alternatives": ["👥", "👫"],
                "confidence": 0.85,
                "category": "pronoun",
                "notes": "Multiple people, not including signer"
            },
            "WHO": {
                "emoji": "🤔",
                "lottie": "question_who.json",
                "alternatives": ["❓", "👤"],
                "confidence": 0.90,
                "category": "question",
                "notes": "Question marker for person"
            },

            "YESTERDAY": {
                "emoji": "⬅️",
                "lottie": "time_yesterday.json",
                "alternatives": ["📅", "⏪", "🕰️"],
                "confidence": 0.85,
                "category": "time",
                "notes": "Backward movement marker for past"
            },
            "TODAY": {
                "emoji": "📅",
                "lottie": "time_today.json",
                "alternatives": ["☀️", "🕐"],
                "confidence": 0.95,
                "category": "time",
                "notes": "Neutral position for present day"
            },
            "TOMORROW": {
                "emoji": "⏩",
                "lottie": "time_tomorrow.json",
                "alternatives": ["➡️", "🌅", "📅"],
                "confidence": 0.85,
                "category": "time",
                "notes": "Forward movement marker for future"
            },
            "NOW": {
                "emoji": "⏱️",
                "lottie": "time_now.json",
                "alternatives": ["🕐", "⌚"],
                "confidence": 0.90,
                "category": "time",
                "notes": "Present moment marker"
            },
            "PAST": {
                "emoji": "📜",
                "lottie": "time_past.json",
                "alternatives": ["⬅️", "🕰️"],
                "confidence": 0.85,
                "category": "time",
                "notes": "Historical past reference"
            },
            "FUTURE": {
                "emoji": "🔮",
                "lottie": "time_future.json",
                "alternatives": ["⏩", "🌅"],
                "confidence": 0.80,
                "category": "time",
                "notes": "General future reference"
            },
            "MORNING": {
                "emoji": "🌅",
                "lottie": "time_morning.json",
                "alternatives": ["☀️", "🌄"],
                "confidence": 0.95,
                "category": "time",
                "notes": "Sunrise marker"
            },
            "AFTERNOON": {
                "emoji": "🌞",
                "lottie": "time_afternoon.json",
                "alternatives": ["☀️", "⛅"],
                "confidence": 0.90,
                "category": "time",
                "notes": "High sun position"
            },
            "EVENING": {
                "emoji": "🌆",
                "lottie": "time_evening.json",
                "alternatives": ["🌇", "🌙"],
                "confidence": 0.95,
                "category": "time",
                "notes": "Sunset marker"
            },
            "NIGHT": {
                "emoji": "🌙",
                "lottie": "time_night.json",
                "alternatives": ["🌃", "⭐"],
                "confidence": 0.95,
                "category": "time",
                "notes": "Moon marker"
            },

            "HOME": {
                "emoji": "🏠",
                "lottie": "location_home.json",
                "alternatives": ["🏡", "🏘️", "🏚️"],
                "confidence": 0.98,
                "category": "location",
                "notes": "Residence, house sign"
            },
            "SCHOOL": {
                "emoji": "🏫",
                "lottie": "location_school.json",
                "alternatives": ["📚", "🎒"],
                "confidence": 0.98,
                "category": "location",
                "notes": "Educational institution"
            },
            "OFFICE": {
                "emoji": "🏢",
                "lottie": "location_office.json",
                "alternatives": ["💼", "🖥️"],
                "confidence": 0.95,
                "category": "location",
                "notes": "Workplace, office building"
            },
            "HOSPITAL": {
                "emoji": "🏥",
                "lottie": "location_hospital.json",
                "alternatives": ["⚕️", "💊"],
                "confidence": 0.98,
                "category": "location",
                "notes": "Medical facility"
            },
            "MARKET": {
                "emoji": "🏪",
                "lottie": "location_market.json",
                "alternatives": ["🛒", "🛍️"],
                "confidence": 0.90,
                "category": "location",
                "notes": "Shopping area, bazaar"
            },
            "PARK": {
                "emoji": "🌳",
                "lottie": "location_park.json",
                "alternatives": ["🌲", "🌴"],
                "confidence": 0.95,
                "category": "location",
                "notes": "Recreational area with trees"
            },
            "TEMPLE": {
                "emoji": "🕉️",
                "lottie": "location_temple.json",
                "alternatives": ["⛪", "🕌"],
                "confidence": 0.90,
                "category": "location",
                "notes": "Religious place (culturally relevant for India)"
            },
            "ROAD": {
                "emoji": "🛣️",
                "lottie": "location_road.json",
                "alternatives": ["🚗", "🛤️"],
                "confidence": 0.90,
                "category": "location",
                "notes": "Path, street, route"
            },
            "HERE": {
                "emoji": "👇",
                "lottie": "location_here.json",
                "alternatives": ["☝️", "📍"],
                "confidence": 0.95,
                "category": "location",
                "notes": "Proximal location (near signer)"
            },
            "THERE": {
                "emoji": "👉",
                "lottie": "location_there.json",
                "alternatives": ["☝️", "📍"],
                "confidence": 0.90,
                "category": "location",
                "notes": "Distal location (far from signer)"
            },

            "EAT": {
                "emoji": "🍽️",
                "lottie": "action_eat.json",
                "alternatives": ["🥄", "👄"],
                "confidence": 0.98,
                "category": "action",
                "notes": "Fingers to mouth, depicting action"
            },
            "DRINK": {
                "emoji": "🥤",
                "lottie": "action_drink.json",
                "alternatives": ["🍷", "💧"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Cup to mouth gesture"
            },
            "SLEEP": {
                "emoji": "😴",
                "lottie": "action_sleep.json",
                "alternatives": ["🛌", "🌙"],
                "confidence": 0.98,
                "category": "action",
                "notes": "Head resting on hands"
            },
            "WAKE": {
                "emoji": "👁️",
                "lottie": "action_wake.json",
                "alternatives": ["😴", "🌅"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Eyes opening gesture"
            },
            "GO": {
                "emoji": "🚶",
                "lottie": "action_go.json",
                "alternatives": ["➡️", "🏃"],
                "confidence": 0.98,
                "category": "action",
                "notes": "Movement away (spatial verb)"
            },
            "COME": {
                "emoji": "🤲",
                "lottie": "action_come.json",
                "alternatives": ["⬅️", "🫴"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Movement toward (spatial verb)"
            },
            "WALK": {
                "emoji": "🚶",
                "lottie": "action_walk.json",
                "alternatives": ["🏃", "👣"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Regular movement"
            },
            "RUN": {
                "emoji": "🏃",
                "lottie": "action_run.json",
                "alternatives": ["💨", "⚡"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Fast movement"
            },
            "SIT": {
                "emoji": "🪑",
                "lottie": "action_sit.json",
                "alternatives": ["💺", "🧘"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Sitting position (classifier verb)"
            },
            "STAND": {
                "emoji": "🧍",
                "lottie": "action_stand.json",
                "alternatives": ["🫀", "⬆️"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Upright position"
            },
            "WORK": {
                "emoji": "💼",
                "lottie": "action_work.json",
                "alternatives": ["🖥️", "🏢"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Employment, labor"
            },
            "WRITE": {
                "emoji": "✍️",
                "lottie": "action_write.json",
                "alternatives": ["📝", "🖊️"],
                "confidence": 0.98,
                "category": "action",
                "notes": "Pencil to paper depicting"
            },
            "READ": {
                "emoji": "📖",
                "lottie": "action_read.json",
                "alternatives": ["📚", "👁️"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Eyes looking at object"
            },
            "LEARN": {
                "emoji": "🧠",
                "lottie": "action_learn.json",
                "alternatives": ["📚", "💡"],
                "confidence": 0.85,
                "category": "action",
                "notes": "Mind/brain focus"
            },
            "TEACH": {
                "emoji": "👨‍🏫",
                "lottie": "action_teach.json",
                "alternatives": ["📚", "✋"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Instruction to another"
            },
            "THINK": {
                "emoji": "🤔",
                "lottie": "action_think.json",
                "alternatives": ["💭", "🧠"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Thought process"
            },
            "KNOW": {
                "emoji": "✅",
                "lottie": "action_know.json",
                "alternatives": ["🧠", "💡"],
                "confidence": 0.85,
                "category": "action",
                "notes": "Knowledge affirmation"
            },
            "WANT": {
                "emoji": "🤲",
                "lottie": "action_want.json",
                "alternatives": ["🙏", "🤞"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Reaching gesture (depicting)"
            },
            "LIKE": {
                "emoji": "👍",
                "lottie": "action_like.json",
                "alternatives": ["❤️", "😍"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Affirmation, approval"
            },
            "LOVE": {
                "emoji": "❤️",
                "lottie": "action_love.json",
                "alternatives": ["😍", "🤗"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Hands over heart gesture"
            },
            "HATE": {
                "emoji": "👎",
                "lottie": "action_hate.json",
                "alternatives": ["😠", "🚫"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Rejection, disapproval"
            },
            "GIVE": {
                "emoji": "🤲",
                "lottie": "action_give.json",
                "alternatives": ["🫴", "📤"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Directional verb (1→2)"
            },
            "TAKE": {
                "emoji": "🤏",
                "lottie": "action_take.json",
                "alternatives": ["✋", "🫴"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Grasping gesture"
            },
            "HELP": {
                "emoji": "🤝",
                "lottie": "action_help.json",
                "alternatives": ["👐", "🙏"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Assistance gesture"
            },
            "DRIVE": {
                "emoji": "🚗",
                "lottie": "action_drive.json",
                "alternatives": ["🛣️", "🏎️"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Steering wheel classifier"
            },
            "PLAY": {
                "emoji": "🎮",
                "lottie": "action_play.json",
                "alternatives": ["🎲", "⚽"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Recreation activity"
            },
            "LAUGH": {
                "emoji": "😂",
                "lottie": "action_laugh.json",
                "alternatives": ["😄", "🤣"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Joyful reaction"
            },
            "CRY": {
                "emoji": "😭",
                "lottie": "action_cry.json",
                "alternatives": ["😢", "🥺"],
                "confidence": 0.95,
                "category": "action",
                "notes": "Tears, emotional reaction"
            },
            "DANCE": {
                "emoji": "🕺",
                "lottie": "action_dance.json",
                "alternatives": ["💃", "🎵"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Rhythmic movement"
            },
            "SING": {
                "emoji": "🎤",
                "lottie": "action_sing.json",
                "alternatives": ["🎵", "🎶"],
                "confidence": 0.90,
                "category": "action",
                "notes": "Vocalization gesture"
            },

            "FOOD": {
                "emoji": "🍱",
                "lottie": "object_food.json",
                "alternatives": ["🍎", "🥗"],
                "confidence": 0.95,
                "category": "object",
                "notes": "Edible items"
            },
            "PIZZA": {
                "emoji": "🍕",
                "lottie": "object_pizza.json",
                "alternatives": ["🍔", "🍱"],
                "confidence": 0.98,
                "category": "object",
                "notes": "Triangular depicting for pizza slice"
            },
            "WATER": {
                "emoji": "💧",
                "lottie": "object_water.json",
                "alternatives": ["🌊", "💦"],
                "confidence": 0.95,
                "category": "object",
                "notes": "Liquid element"
            },
            "BOOK": {
                "emoji": "📚",
                "lottie": "object_book.json",
                "alternatives": ["📖", "📝"],
                "confidence": 0.98,
                "category": "object",
                "notes": "Reading material"
            },
            "CAR": {
                "emoji": "🚗",
                "lottie": "object_car.json",
                "alternatives": ["🚙", "🏎️"],
                "confidence": 0.95,
                "category": "object",
                "notes": "Vehicle (3-hand classifier)"
            },
            "PHONE": {
                "emoji": "📱",
                "lottie": "object_phone.json",
                "alternatives": ["☎️", "📞"],
                "confidence": 0.95,
                "category": "object",
                "notes": "Communication device"
            },
            "COMPUTER": {
                "emoji": "💻",
                "lottie": "object_computer.json",
                "alternatives": ["🖥️", "⌨️"],
                "confidence": 0.95,
                "category": "object",
                "notes": "Digital device"
            },
            "MONEY": {
                "emoji": "💰",
                "lottie": "object_money.json",
                "alternatives": ["💵", "💴"],
                "confidence": 0.90,
                "category": "object",
                "notes": "Currency, wealth"
            },
            "BALL": {
                "emoji": "⚽",
                "lottie": "object_ball.json",
                "alternatives": ["🏀", "🎾"],
                "confidence": 0.95,
                "category": "object",
                "notes": "Spherical object"
            },

            "HAPPY": {
                "emoji": "😊",
                "lottie": "emotion_happy.json",
                "alternatives": ["😄", "😁"],
                "confidence": 0.98,
                "category": "emotion",
                "notes": "Joy, positive emotion"
            },
            "SAD": {
                "emoji": "😢",
                "lottie": "emotion_sad.json",
                "alternatives": ["😞", "😔"],
                "confidence": 0.98,
                "category": "emotion",
                "notes": "Sorrow, negative emotion"
            },
            "ANGRY": {
                "emoji": "😠",
                "lottie": "emotion_angry.json",
                "alternatives": ["😡", "🤬"],
                "confidence": 0.95,
                "category": "emotion",
                "notes": "Anger, rage"
            },
            "SCARED": {
                "emoji": "😨",
                "lottie": "emotion_scared.json",
                "alternatives": ["😱", "😰"],
                "confidence": 0.95,
                "category": "emotion",
                "notes": "Fear, anxiety"
            },
            "SURPRISED": {
                "emoji": "😮",
                "lottie": "emotion_surprised.json",
                "alternatives": ["😲", "🤩"],
                "confidence": 0.90,
                "category": "emotion",
                "notes": "Shock, astonishment"
            },
            "TIRED": {
                "emoji": "😴",
                "lottie": "emotion_tired.json",
                "alternatives": ["😫", "🥱"],
                "confidence": 0.90,
                "category": "emotion",
                "notes": "Fatigue, exhaustion"
            },
            "CONFUSED": {
                "emoji": "🤔",
                "lottie": "emotion_confused.json",
                "alternatives": ["😕", "❓"],
                "confidence": 0.85,
                "category": "emotion",
                "notes": "Uncertainty, puzzlement"
            },
            "GOOD": {
                "emoji": "✅",
                "lottie": "descriptor_good.json",
                "alternatives": ["👍", "😊"],
                "confidence": 0.90,
                "category": "descriptor",
                "notes": "Positive quality"
            },
            "BAD": {
                "emoji": "❌",
                "lottie": "descriptor_bad.json",
                "alternatives": ["👎", "😞"],
                "confidence": 0.90,
                "category": "descriptor",
                "notes": "Negative quality"
            },
            "BIG": {
                "emoji": "📏",
                "lottie": "descriptor_big.json",
                "alternatives": ["🔆", "⬆️"],
                "confidence": 0.90,
                "category": "descriptor",
                "notes": "Size modifier (hands apart)"
            },
            "SMALL": {
                "emoji": "📌",
                "lottie": "descriptor_small.json",
                "alternatives": ["🔅", "⬇️"],
                "confidence": 0.90,
                "category": "descriptor",
                "notes": "Size modifier (hands together)"
            },
            "HOT": {
                "emoji": "🔥",
                "lottie": "descriptor_hot.json",
                "alternatives": ["🌡️", "😰"],
                "confidence": 0.90,
                "category": "descriptor",
                "notes": "Temperature/intensity"
            },
            "COLD": {
                "emoji": "❄️",
                "lottie": "descriptor_cold.json",
                "alternatives": ["🥶", "🌨️"],
                "confidence": 0.90,
                "category": "descriptor",
                "notes": "Low temperature"
            },

            "QUESTION": {
                "emoji": "❓",
                "lottie": "marker_question.json",
                "alternatives": ["🤔", "?"],
                "confidence": 0.95,
                "category": "marker",
                "notes": "Question marker (brow raise + sign)"
            },
            "NOT": {
                "emoji": "❌",
                "lottie": "marker_not.json",
                "alternatives": ["🚫", "🙅"],
                "confidence": 0.95,
                "category": "marker",
                "notes": "Negation (head shake + sign)"
            },
            "WHAT": {
                "emoji": "🤷",
                "lottie": "question_what.json",
                "alternatives": ["❓", "🤔"],
                "confidence": 0.90,
                "category": "question",
                "notes": "WH-word for object"
            },
            "WHERE": {
                "emoji": "🗺️",
                "lottie": "question_where.json",
                "alternatives": ["📍", "🧭"],
                "confidence": 0.90,
                "category": "question",
                "notes": "WH-word for location"
            },
            "WHEN": {
                "emoji": "🕐",
                "lottie": "question_when.json",
                "alternatives": ["📅", "⏰"],
                "confidence": 0.90,
                "category": "question",
                "notes": "WH-word for time"
            },
            "WHY": {
                "emoji": "🤨",
                "lottie": "question_why.json",
                "alternatives": ["❓", "🤔"],
                "confidence": 0.85,
                "category": "question",
                "notes": "WH-word for reason"
            },
            "HOW": {
                "emoji": "🙌",
                "lottie": "question_how.json",
                "alternatives": ["❓", "🤷"],
                "confidence": 0.85,
                "category": "question",
                "notes": "WH-word for manner"
            },

            "HELLO": {
                "emoji": "👋",
                "lottie": "social_hello.json",
                "alternatives": ["🤝", "👐"],
                "confidence": 0.98,
                "category": "social",
                "notes": "Greeting sign (wave)"
            },
            "GOODBYE": {
                "emoji": "👋",
                "lottie": "social_goodbye.json",
                "alternatives": ["🤝", "🙏"],
                "confidence": 0.95,
                "category": "social",
                "notes": "Farewell (wave or spread hands)"
            },
            "PLEASE": {
                "emoji": "🙏",
                "lottie": "social_please.json",
                "alternatives": ["🥺", "😔"],
                "confidence": 0.95,
                "category": "social",
                "notes": "Request politeness marker"
            },
            "THANK": {
                "emoji": "🙏",
                "lottie": "social_thank.json",
                "alternatives": ["👏", "❤️"],
                "confidence": 0.95,
                "category": "social",
                "notes": "Gratitude expression"
            },
            "SORRY": {
                "emoji": "😔",
                "lottie": "social_sorry.json",
                "alternatives": ["🙏", "😞"],
                "confidence": 0.95,
                "category": "social",
                "notes": "Apology expression"
            },
            "YES": {
                "emoji": "👍",
                "lottie": "social_yes.json",
                "alternatives": ["✅", "🤓"],
                "confidence": 0.95,
                "category": "social",
                "notes": "Affirmation (nodding)"
            },
            "NO": {
                "emoji": "🙅",
                "lottie": "social_no.json",
                "alternatives": ["👎", "❌"],
                "confidence": 0.95,
                "category": "social",
                "notes": "Negation (head shake)"
            },

            "MOTHER": {
                "emoji": "👩",
                "lottie": "family_mother.json",
                "alternatives": ["👶", "🤱"],
                "confidence": 0.95,
                "category": "family",
                "notes": "Female parent"
            },
            "FATHER": {
                "emoji": "👨",
                "lottie": "family_father.json",
                "alternatives": ["👶", "🧔"],
                "confidence": 0.95,
                "category": "family",
                "notes": "Male parent"
            },
            "BROTHER": {
                "emoji": "👦",
                "lottie": "family_brother.json",
                "alternatives": ["👨", "🧑"],
                "confidence": 0.90,
                "category": "family",
                "notes": "Male sibling"
            },
            "SISTER": {
                "emoji": "👧",
                "lottie": "family_sister.json",
                "alternatives": ["👩", "🧑"],
                "confidence": 0.90,
                "category": "family",
                "notes": "Female sibling"
            },
            "FRIEND": {
                "emoji": "👫",
                "lottie": "family_friend.json",
                "alternatives": ["🤝", "❤️"],
                "confidence": 0.90,
                "category": "family",
                "notes": "Social companion"
            },

            "CL-3": {
                "emoji": "🚗",
                "lottie": "classifier_3hand.json",
                "alternatives": ["✌️", "👌"],
                "confidence": 0.85,
                "category": "classifier",
                "notes": "3-hand classifier for vehicles"
            },
            "CL-5": {
                "emoji": "👋",
                "lottie": "classifier_5hand.json",
                "alternatives": ["👐", "🙌"],
                "confidence": 0.85,
                "category": "classifier",
                "notes": "5-hand classifier for flat objects/animals"
            },
            "CL-1": {
                "emoji": "☝️",
                "lottie": "classifier_1hand.json",
                "alternatives": ["🫴", "👆"],
                "confidence": 0.85,
                "category": "classifier",
                "notes": "1-hand classifier for people/upright objects"
            },
            "BROW-RAISE": {
                "emoji": "🤨",
                "lottie": "facial_brow_raise.json",
                "alternatives": ["😮", "🤩"],
                "confidence": 0.90,
                "category": "facial_expression",
                "notes": "Facial marker for questions"
            },
            "HEAD-SHAKE": {
                "emoji": "🙅",
                "lottie": "facial_head_shake.json",
                "alternatives": ["❌", "👎"],
                "confidence": 0.90,
                "category": "facial_expression",
                "notes": "Facial marker for negation"
            },
            "HEAD-NOD": {
                "emoji": "🙋",
                "lottie": "facial_head_nod.json",
                "alternatives": ["✅", "👍"],
                "confidence": 0.90,
                "category": "facial_expression",
                "notes": "Facial marker for affirmation"
            },
        }

    def map_gloss(self, gloss_sequence: List[str]) -> List[Dict[str, Any]]:

        results = []
        for word in gloss_sequence:
            word_upper = word.upper()

            if word_upper in self.dictionary:
                entry = self.dictionary[word_upper]
                results.append({
                    "word": word_upper,
                    "emoji": entry["emoji"],
                    "confidence": entry["confidence"],
                    "category": entry["category"],
                    "method": "exact",
                    "alternatives": entry.get("alternatives", []),
                    "lottie_file": entry.get("lottie"),
                    "notes": entry.get("notes", "")
                })
                continue

            fallback_emoji = "❔"
            if word_upper.isupper() and len(word_upper) > 2:
                fallback_emoji = "👤"  

            results.append({
                "word": word_upper,
                "emoji": fallback_emoji,
                "confidence": 0.3,
                "category": "unknown",
                "method": "fallback",
                "alternatives": [],
                "lottie_file": None,
                "notes": "Not found in ISL dictionary - consider adding"
            })

        return results

isl_emoji_mapper = ISLEmojiMapper()
