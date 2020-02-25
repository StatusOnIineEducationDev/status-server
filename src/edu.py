class TransportCmd:
    TestCommand = 100
    ConcentrationFinalData = 101
    StudentCameraFrameData = 102
    CreateLesson = 103
    JoinInLesson = 104
    BeginLesson = 105
    PaintCommand = 106
    CreatePaintConnection = 107
    CreateCVServerConnection = 108
    EndLesson = 109
    SendChatContent = 110
    RecvChatContent = 111
    ChatBan = 112
    RaiseHand = 113
    ResultOfRaiseHand = 114
    RemoveMemberFromInSpeech = 115
    ConcentrationRealTimeData = 116
    QuitLesson = 117


class ErrorCode:
    NoError = 0
    InSpeechError = 1
    ApplyingError = 2
    AccountTypeError = 3
    AccountNotFoundError = 4
    PasswordError = 5
    CourseResourceTitleDuplicateError = 6
    CourseResourceNotFoundError = 7
    CourseNotFoundError = 8


class CourseStatus:
    OffLine = 0
    OnLine = 1
    CantJoinIn = 2
    Waiting = 3


class ChatStatus:
    Free = 0
    Baned = 1


class UserStatus:
    Free = 0
    InRoom = 1
    InClass = 2


class ApplicationStatus:
    Accepted = 0
    Refused = 1
    HungUp = 2


class SpeechStatus:
    SpeechFree = 0
    InSpeech = 1
    Applying = 2


class AccountType:
    Teacher = 0
    Student = 1


class Emotion:
    Angry = 0
    Disgust = 1
    Fear = 2
    Happy = 3
    Sad = 4
    Surprise = 5
    Neutral = 6
