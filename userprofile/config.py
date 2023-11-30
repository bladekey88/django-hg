# Labels
class Default(object):
    class DefaultLabel:
        EMAIL: str = "Email Address"
        UID: str = "Username"
        IDNUMBER: str = "ID Number"
        IS_SYSTEM_STAFF: str = "Access Managed Area"
        IS_ACTIVE: str = "Is Active"
        DATE_CREATED: str = "Date Created"
        DATE_MODIFIED: str = "Date Modified"
        DATE_JOINED: str = "Date Joined"
        LAST_LOGIN: str = "Last Logged In"
        FIRST_NAME: str = "First Name"
        MIDDLE_NAME: str = "Middle Name"
        LAST_NAME: str = "Last Name"
        COMMON_NAME: str = "Preferred Name"
        SEX: str = "Sex"
        TITLE: str = "Title"
        STAFF_MEMBER: str = "Staff Member"
        STAFF_MEMBER_PLURAL: str = "Staff Members"
        IS_HEAD_OF_HOUSE: str = "Is Head Of House"
        STUDENT: str = "Student"
        STUDENT_PLURAL: str = "Students"
        HOUSE: str = "House"
        YEAR: str = "Year"
        IS_PREFECT: str = "Is Prefect"
        PARENT: str = "Parent"
        PARENT_PLURAL: str = "Parents"
        PARENT_CHILDREN: str = "Children"

    class DefaultGroup:
        ALL_USERS = "All Users"
        ALL_STAFF = "All Staff"
        ALL_STUDENT = "All Students"
        ALL_PARENT = "All Parents"
        HEADS_OF_HOUSE_GROUP = "Heads of House"

    class DefaultConfig:
        STUDENT_MIN_YEAR_VALIDATOR: int = 1
        STUDENT_MAX_YEAR_VALIDATOR: int = 7


class Label(Default.DefaultLabel):
    @classmethod
    def all(cls):
        labels = {}
        for label_code, label in vars(Default.DefaultLabel).items():
            if label_code.isupper():
                labels[label_code] = {"label": label, "default": True}

        for label_code, label in vars(cls).items():
            if label_code.isupper():
                if label_code in labels:
                    # Overwrite the default label with the custom label.
                    labels[label_code] = {"label": label, "default": False}
                else:
                    # Add the custom label to the dictionary.
                    labels[label_code] = {"label": label, "default": False}

        return labels


class Config(Default.DefaultConfig):
    pass


class ConfigGroup(Default.DefaultGroup):
    pass
