# Weather Alert Visualization System
# CMPSC 132 - Programming & Computation 2


class WeatherAlert:
    # maps severity number to a word
    SEVERITY_LABELS = {
        1: "Minor",
        2: "Moderate",
        3: "Severe",
        4: "Extreme",
        5: "Catastrophic"
    }

    # maps alert type to an emoji
    TYPE_ICONS = {
        "tornado":      "🌪️ ",
        "flood":        "🌊",
        "blizzard":     "❄️ ",
        "hurricane":    "🌀",
        "wildfire":     "🔥",
        "heatwave":     "☀️ ",
        "thunderstorm": "⛈️ ",
    }

    def __init__(self, alert_type, severity, location, message):
        if severity < 1 or severity > 5:
            raise ValueError("Severity must be between 1 and 5.")
        self.alert_type = alert_type
        self.severity   = severity
        self.location   = location
        self.message    = message

    def get_severity_label(self):
        return self.SEVERITY_LABELS.get(self.severity, "Unknown")

    def get_icon(self):
        return self.TYPE_ICONS.get(self.alert_type.lower(), "⚠️ ")

    def __str__(self):
        filled = "█" * self.severity
        empty  = "░" * (5 - self.severity)
        bar    = filled + empty
        icon   = self.get_icon()
        return (
            f"  {icon}  [{self.alert_type.upper()}]  —  {self.location}\n"
            f"       Severity : {bar}  {self.severity}/5  ({self.get_severity_label()})\n"
            f"       Message  : {self.message}"
        )


class Node:
    def __init__(self, alert):
        self.alert = alert
        self.next  = None


class LinkedList:
    def __init__(self):
        self.head  = None
        self._size = 0

    def is_empty(self):
        return self._size == 0

    def size(self):
        return self._size

    def to_list(self):
        result  = []
        current = self.head
        while current:
            result.append(current.alert)
            current = current.next
        return result

    def display_recursive(self, node=None, index=1, first_call=True):
        # start at the head on the first call
        if first_call:
            node = self.head

        # nothing left to print
        if node is None:
            return

        print(f"\n  Alert #{index}")
        print(node.alert)
        print(f"  {'─'*52}")

        self.display_recursive(node.next, index + 1, first_call=False)

    def search_by_type(self, alert_type, node=None, first_call=True):
        if first_call:
            node = self.head

        # end of list, return empty
        if node is None:
            return []

        matches = []
        if node.alert.alert_type.lower() == alert_type.lower():
            matches.append(node.alert)

        return matches + self.search_by_type(alert_type, node.next, first_call=False)

    def search_by_min_severity(self, min_sev, node=None, first_call=True):
        if first_call:
            node = self.head

        if node is None:
            return []

        matches = []
        if node.alert.severity >= min_sev:
            matches.append(node.alert)

        return matches + self.search_by_min_severity(min_sev, node.next, first_call=False)


class AlertQueue(LinkedList):
    # queue uses FIFO — first alert in is the first one dispatched

    def __init__(self):
        super().__init__()
        self.tail = None

    def enqueue(self, alert):
        new_node = Node(alert)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail      = new_node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            return None
        alert     = self.head.alert
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return alert

    def peek(self):
        if self.is_empty():
            return None
        return self.head.alert


class AlertStack(LinkedList):
    # stack keeps track of what was already dispatched, most recent on top

    def push(self, alert):
        new_node      = Node(alert)
        new_node.next = self.head
        self.head     = new_node
        self._size   += 1

    def pop(self):
        if self.is_empty():
            return None
        alert     = self.head.alert
        self.head = self.head.next
        self._size -= 1
        return alert

    def peek(self):
        if self.is_empty():
            return None
        return self.head.alert


def insertion_sort_by_severity(alerts, descending=True):
    # sort a copy so we don't mess up the original list
    sorted_alerts = alerts[:]
    for i in range(1, len(sorted_alerts)):
        key = sorted_alerts[i]
        j   = i - 1
        if descending:
            while j >= 0 and sorted_alerts[j].severity < key.severity:
                sorted_alerts[j + 1] = sorted_alerts[j]
                j -= 1
        else:
            while j >= 0 and sorted_alerts[j].severity > key.severity:
                sorted_alerts[j + 1] = sorted_alerts[j]
                j -= 1
        sorted_alerts[j + 1] = key
    return sorted_alerts


class AlertSystem:
    def __init__(self, system_name="National Weather Alert System"):
        self.system_name = system_name
        self.queue       = AlertQueue()
        self.history     = AlertStack()
        self.region_map  = {}  # tracks which alert types showed up per location

    def add_alert(self, alert_type, severity, location, message):
        alert = WeatherAlert(alert_type, severity, location, message)
        self.queue.enqueue(alert)

        if location not in self.region_map:
            self.region_map[location] = []
        self.region_map[location].append(alert_type)

        print(f"  ✔  Added: [{alert_type.upper()}] in {location}  (Severity {severity})")

    def display_all(self):
        print(f"\n{'═'*55}")
        print(f"  🌩   {self.system_name}")
        print(f"  Active Alerts in Queue: {self.queue.size()}")
        print(f"{'═'*55}")

        if self.queue.is_empty():
            print("  No active alerts at this time.\n")
        else:
            self.queue.display_recursive()
        print()

    def display_sorted(self):
        print(f"\n{'═'*55}")
        print("  📊  Alerts Sorted by Severity  (High → Low)")
        print(f"{'═'*55}")

        alerts = self.queue.to_list()
        if not alerts:
            print("  No active alerts.\n")
            return

        sorted_alerts = insertion_sort_by_severity(alerts, descending=True)
        for i, alert in enumerate(sorted_alerts, 1):
            print(f"\n  #{i}")
            print(alert)
            print(f"  {'─'*52}")
        print()

    def filter_by_type(self, alert_type):
        print(f"\n{'═'*55}")
        print(f"  🔍  Filter by Type: {alert_type.title()}")
        print(f"{'═'*55}")

        results = self.queue.search_by_type(alert_type)

        if not results:
            print(f"  No '{alert_type}' alerts found.\n")
        else:
            for i, alert in enumerate(results, 1):
                print(f"\n  #{i}")
                print(alert)
                print(f"  {'─'*52}")
        print()

    def filter_by_severity(self, min_severity):
        label = WeatherAlert.SEVERITY_LABELS.get(min_severity, "?")
        print(f"\n{'═'*55}")
        print(f"  🔍  Filter: Severity ≥ {min_severity}  ({label}+)")
        print(f"{'═'*55}")

        results = self.queue.search_by_min_severity(min_severity)

        if not results:
            print(f"  No alerts with severity ≥ {min_severity}.\n")
        else:
            for i, alert in enumerate(results, 1):
                print(f"\n  #{i}")
                print(alert)
                print(f"  {'─'*52}")
        print()

    def process_next(self):
        print(f"\n{'═'*55}")
        print("  🚨  Dispatching Next Alert")
        print(f"{'═'*55}")

        alert = self.queue.dequeue()
        if alert is None:
            print("  Queue is empty — nothing to dispatch.\n")
        else:
            self.history.push(alert)
            print(f"\n  ✔  Dispatched:")
            print(alert)
            print(f"\n  Remaining in queue : {self.queue.size()}")
            print(f"  History stack size : {self.history.size()}")
        print()

    def undo_last_dispatch(self):
        # pops the most recently dispatched alert and puts it back at the front
        print(f"\n{'═'*55}")
        print("  ↩️   Undoing Last Dispatch")
        print(f"{'═'*55}")

        alert = self.history.pop()
        if alert is None:
            print("  Nothing to undo.\n")
        else:
            restored_node      = Node(alert)
            restored_node.next = self.queue.head
            self.queue.head    = restored_node
            if self.queue.tail is None:
                self.queue.tail = restored_node
            self.queue._size  += 1

            print(f"\n  ✔  Restored to front of queue:")
            print(alert)
            print(f"\n  Queue size now : {self.queue.size()}")
            print(f"  Stack size now : {self.history.size()}")
        print()

    def display_region_map(self):
        print(f"\n{'═'*55}")
        print("  🗺️   Region  →  Alert Types")
        print(f"{'═'*55}")

        if not self.region_map:
            print("  No region data available.\n")
            return

        for region, types in self.region_map.items():
            unique = list(dict.fromkeys(types))  # remove duplicates, keep order
            print(f"  📍 {region:<25}: {', '.join(unique)}")
        print()

    def summary_stats(self):
        active    = self.queue.to_list()
        processed = self.history.to_list()

        print(f"\n{'═'*55}")
        print("  📈  Summary Statistics")
        print(f"{'═'*55}")
        print(f"  Active in queue   : {len(active)}")
        print(f"  Total dispatched  : {len(processed)}")

        if active:
            sevs = [a.severity for a in active]
            print(f"\n  — Active Alert Stats —")
            print(f"  Average severity  : {sum(sevs) / len(sevs):.1f} / 5")
            print(f"  Highest severity  : {max(sevs)}")
            print(f"  Lowest severity   : {min(sevs)}")

            type_count = {}
            for a in active:
                type_count[a.alert_type] = type_count.get(a.alert_type, 0) + 1
            print(f"\n  Alert type breakdown:")
            for t, count in type_count.items():
                print(f"    {t:<16} : {count} alert(s)")

        if processed:
            print(f"\n  — Dispatch History (most recent on top) —")
            for i, a in enumerate(processed, 1):
                print(f"  #{i:<3} [{a.alert_type.upper():<13}]  {a.location}  (Sev {a.severity})")
        print()


# sample data below — not part of the core program, just for testing
system = AlertSystem("Central US Weather Alert System")

print("\n" + "═"*55)
print("  🌪   Weather Alert Visualization System")
print("  CMPSC 132 — Final Project")
print("═"*55 + "\n")

print("  Loading sample alerts...\n")
sample_alerts = [
    ("Tornado",   5, "Oklahoma City, OK", "EF4 tornado on the ground. Seek shelter immediately."),
    ("Flood",     4, "Houston, TX",        "Flash flooding on I-10. Avoid all low-lying areas."),
    ("Blizzard",  4, "Denver, CO",         "Blizzard warning: 18+ inches of snow expected overnight."),
    ("Hurricane", 5, "New Orleans, LA",    "Category 4 landfall expected within 12 hours."),
]

for alert_type, severity, location, message in sample_alerts:
    system.add_alert(alert_type, severity, location, message)

system.display_all()
system.display_sorted()
system.filter_by_type("Tornado")
system.filter_by_severity(4)
system.display_region_map()
system.summary_stats()
system.process_next()
system.process_next()
system.undo_last_dispatch()
system.summary_stats()
