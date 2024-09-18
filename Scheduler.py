from typing import List, Tuple

state_time_zones = {
   "AL": "Central",
   "AK": "Pacific", 
   "AZ": "Pacific", 
   "AR": "Mountain",
   "CA": "Pacific",
   "CO": "Mountain", 
   "CT": "Eastern",
   "DE": "Eastern",
   "FL": "Eastern",
   "GA": "Eastern",
   "HI": "Pacific", 
   "ID": "Mountain",  
   "IL": "Central",
   "IN": "Eastern",  
   "IA": "Central",
   "KS": "Central",
   "KY": "Eastern", 
   "LA": "Central",
   "ME": "Eastern",
   "MD": "Eastern",
   "MA": "Eastern",
   "MI": "Eastern", 
   "MN": "Central",
   "MS": "Central",
   "MO": "Central",
   "MT": "Mountain",  
   "NE": "Central",  
   "NV": "Pacific",
   "NH": "Eastern",
   "NJ": "Eastern",
   "NM": "Mountain", 
   "NY": "Eastern",
   "NC": "Eastern",
   "ND": "Central",
   "OH": "Eastern",
   "OK": "Central",
   "OR": "Pacific",
   "PA": "Eastern",
   "RI": "Eastern",
   "SC": "Eastern",
   "SD": "Central",
   "TN": "Central",
   "TX": "Central",
   "UT": "Mountain", 
   "VT": "Eastern",
   "VA": "Eastern",
   "WA": "Pacific",
   "WV": "Eastern",
   "WI": "Central",
   "WY": "Mountain" 
}


class TeamMember:
    def __init__(self, name: str, availability: List[Tuple[int, int]], state: str, seniority: int):
        self.name = name
        self.availability = availability
        self.state = state
        self.seniority = seniority
    
    def getName(self) -> str:
        """Return the name of the team member."""
        return self.name


    def getAvailability(self) -> List[Tuple[int, int]]:
        """Return the availability of the team member."""
        return self.availability


    def getState(self) -> int:
        """Return the state of the team member."""
        return self.state


    def getSeniority(self) -> int:
        """Return the seniority of the team member, which is based on seniority."""
        return self.seniority
    
    # Functions Added by AJ
    def getTimeZone(self) -> str:
        """Return the time zone of the member"""
        return state_time_zones[self.state]
    
    def getAvailabilityPacific (self) -> List[Tuple[int, int]]:
        """Returns the members availability in Pacific time"""
        if self.getTimeZone() == "Pacific":
            return self.availability
        elif self.getTimeZone() == "Mountain":
            shift = -1
        elif self.getTimeZone() == "Central":
            shift = -2
        elif self.getTimeZone() == "Eastern":
            shift = -3
        return self.getAvailabilityShift(shift)

    def getAvailabilityShift(self, shift) -> List[Tuple[int, int]]:
        """Returns the availability of the member after a given  time zone shift"""
        new_availability = []
        for i in self.availability:
            new_start = i[0] + shift
            new_end = i[1] + shift
            if new_start < 0:
                new_start += 24
            if new_end < 0:
                new_end += 24
            new_availability.append((new_start, new_end))
        return new_availability
    
    def __str__(self) -> str:
        """String Representation of the CLass"""
        return (f"TeamMember(name={self.name}, "
                f"availability={self.availability}, "
                f"state={self.state}, "
                f"seniority={self.seniority})")
    
    def __repr__ (self) -> str:
        """returns the member's name"""
        return self.name


class Scheduler:
    def __init__(self, meeting_time: int, team_members: List[TeamMember], time_zone = "Pacific"):
        """Initialize with the desired meeting time and time zone"""
        self.meeting_time = meeting_time
        self.team_members = team_members
        if time_zone in ["Pacific", "Mountain", "Central", "Eastern"]:
           self.time_zone = time_zone
        else:
           raise Exception("Only Pacific, Mountain, Central, and Eastern time zones are acceptable")


    def find_optimal_time(self, team_members: List[TeamMember], feedback_length = 1, seniority_score = lambda x:x):
        """
        Finds the best times  for a meeting by checking the availability of the team members and 
        returning a list of time slots sorted by which work best with the given members schedules 
        and a dictionary including information on members attenndence and score.
        """
        D = {}

        # define the shift necessary to display the time in the given time zone
        if self.time_zone == "Pacific":
            shift = 0
        elif self.time_zone == "Mountain":
            shift = 1
        elif self.time_zone == "Central":
            shift = 2
        else:
            shift = 3

        #itearates through the team members
        for member in team_members:
            for slot in member.getAvailabilityPacific():
                for i in range(slot[0], slot[1]):
                    for j in range(0, self.meeting_time):
                        # Defines the start time of the meeting
                        if (i-j) + shift < 0:
                            meeting_start = (i-j) + shift + 24
                        else:
                            meeting_start = (i-j) + shift
                        # Defines the end time of the meeting
                        if meeting_start + self.meeting_time >= 24:
                            meeting_end = meeting_start + self.meeting_time - 24
                        else:
                            meeting_end = meeting_start + self.meeting_time

                        if (meeting_start, meeting_end) in D:
                            #increments the score for the meeting time based on seniority_score function and the member's seniotity
                            D[(meeting_start, meeting_end)]["score"] += seniority_score(member.getSeniority())
                            #adds the member to the function
                            D[(meeting_start, meeting_end)]["members"].add(member)
                        #adds the meeting time ot the dictionary with the initialize score, members, and an empty set of part-time members
                        else:
                            D[(meeting_start, meeting_end)] = {"score":seniority_score(member.getSeniority()), "members":set([member]), "part-time":set([])}

                        # checks if the member must arrive late
                        if (slot[0] + shift > meeting_start and slot[0] + shift < meeting_end):
                            #adds member to part-time section of dict with relevant info
                            D[(meeting_start, meeting_end)]["part-time"].add((member, "arrives late"))
                        # checks if the member must leave early
                        if (slot[1] + shift < meeting_end and slot[0] < slot[1]):
                            #adds member to part-time section of dict with relevant info
                            D[(meeting_start, meeting_end)]["part-time"].add((member, "leaves early"))
        
        #sorts the possible meeting times by their score (best to worst)
        best_times = sorted(D.keys(), key=lambda x : D[x]["score"], reverse=True)
        #returns the sorted list of scores and the dictionary with more info (meeting times are keys)
        return best_times, D
    
    def planMeeting (self, team_members: List[TeamMember], feedback_length = 1, seniority_score = lambda x:x):
        """
        returns a string of easily readable meeting description

        inputs
        ______
        team_members: (List[TeamMember]) all desired members
        feedback_length: (int) the number of meeting times you want returned
        seniority_score: a function that maps 1 to the weight you want to give low seniority and 2 to the  weight for high seniority
        """
        text = ""
        #Runs find_optimal_time to create the list of best times and accompanying dictionary
        best_times, D = self.find_optimal_time(team_members=team_members, feedback_length = feedback_length, seniority_score = seniority_score)
        #Adds the most optimal meeting from the List to the main string output
        text += "The optimal meeting time is from " + str(best_times[0][0]) + " to " + str(best_times[0][1]) + " " + self.time_zone + "\n" + "available: "
        #adds the members in attendance
        for attendee in D[best_times[0]]["members"]:
            text += attendee.__repr__() + " "
        text += "\n"
        #If there are any members who cannot attend the whole meeting they will be added to the string
        if D[best_times[0]]["part-time"]:
            text += "Note that this time will mean that: \n"
            for m in D[best_times[0]]["part-time"]:
                text += m[0].__repr__() + " " +  m[1] + "\n"
        text += "\n"
        #for any subsequent meeting (depending on feedback_length) will print the meeting time and attendance
        for i in range(1, feedback_length):
            text += "The next best time is from " + str(best_times[i][0]) + " to " + str(best_times[i][1]) + " " + self.time_zone + "\n"+ "attending: "
            for attendee in D[best_times[0]]["members"]:
                text += attendee.__repr__() + " "
            text += "\n"
            if D[best_times[i]]["part-time"]:
                text += "Note that this time will mean that: \n"
                for m in D[best_times[i]]["part-time"]:
                    text += m[0].__repr__() + " " +  m[1] + "\n"
            text += "\n"
        #returns the whole string of meeting information
        return text



# Example usage
member1 = TeamMember(name="Alice", availability=[(9, 13), (15, 20)], state="CA", seniority=2)
member2 = TeamMember(name="Bob", availability=[ (8, 12), (13, 14)], state="MD", seniority=1)
member3 = TeamMember(name="Charlie", availability=[(8, 11), (13, 15)], state="NY", seniority=1)


# Create the scheduler with a specific meeting duration in hours
team = [member1, member2, member3]
scheduler = Scheduler(meeting_time=2, team_members=team)

weight_seniority_low = (lambda x: 1 if (x==1) else 0.5)
weight_seniority_high = (lambda x: 1 if (x==1) else 2)
weight_seniority_none = (lambda x:x)


# Find the optimal meeting time
print(scheduler.planMeeting(team, seniority_score= weight_seniority_none, feedback_length = 3))