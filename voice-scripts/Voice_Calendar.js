const homeScreen = visual({"screen": "home"});
const eventsScreen = visual({"screen": "events"});
const newEventScreen = visual({"screen": "new-event"});

onUserEvent((p, e) => {
    console.info('event', JSON.stringify(e));
    if (e.event == 'buttonClicked') {
        p.play({command: 'onButtonClick', activeField: p.visual.activeField})
    }
});

intent('What (screen|page|) am I (viewing|seeing|looking at|on)?', p => {
    let screen = p.visual.screen;
    switch (screen) {
        case "home":
            p.play('This is the Home screen, which gives basic info about the app.');
            break;
        case "events":
            p.play('This is the Events screen, which displays your upcoming calendar events.');
            break;
        case "new-event":
            p.play('This is the New Event screen, where you can create a new calendar event.');
            break;
        default:
            p.play('(Sorry,|) I have no data about this screen');
    }
});

newEventScreen(() => {
    function textInput(field, input) { 
        return "(the|) " + field + " is " + input; 
    }

    function datetimeInput(verb) {
        return "(the|) event " + verb + " $(DATE) at $(TIME)"; 
    }

    function dateInput(verb) {
        return "(the|) event " + verb + " $(DATE)"; 
    }

    function countInput(verb) {
        return "(the|) event " + verb + " $(NUMBER) times"; 
    }

    function capitalize(string) {
        const words = string.split(" ");
        const result = words.map((word) => { 
            return word[0].toUpperCase() + word.substring(1); 
        }).join(" ");
        return result;
    }

    const timezones = "$(TZ~ " + 
            "Pacific Time~America/Los_Angeles|Pacific~America/Los_Angeles|" + 
            "Mountain Time~America/Denver|Mountain~America/Denver|" + 
            "Central Time~America/Chicago|Central~America/Chicago|" + 
            "Eastern Time~America/New_York|Eastern~America/New_York)"

    function mergeDatetime(date, timeSeconds) {
        return date.luxon.plus({ seconds: timeSeconds }).toISO().slice(0, -10);
    }

    function processUntilDate(date) {
        return date.luxon.toISO().slice(0, -19);
    }
    
    function sayDate(date) {
        return date.moment.format("dddd, MMMM Do YYYY");
    }

    function fillFormField(p, field, value) {
        p.play({command: 'fillFormField', field: field, value: value})
    }
    
    function nextField(p, next) {
        p.visual.activeField = next;
        p.play({command: 'nextField', next: next});
    }
    
    let stopRepeat = context(() => {
        intent('(On|Until|) $(DATE)', p => {
            fillFormField(p, 'until', processUntilDate(p.DATE))
            p.play(`The event repeats until ${sayDate(p.DATE)}.`)
            nextField(p, "location");
        });
        intent('After $(NUMBER) (times|occurrences)', p => {
            fillFormField(p, 'count', p.NUMBER.number)
            p.play(`The event repeats ${p.NUMBER.number} times`)
            nextField(p, "location");
        });
    });
    
    let dailyOrWeekly = context(() => {
        intent('Daily', p => {
            fillFormField(p, 'freq', 'DAILY')
            p.play('The event repeats daily.')
            nextField(p, "location");
        });
        intent('Weekly', p => {
            fillFormField(p, 'freq', 'WEEKLY')
            p.play('The event repeats weekly.')
            nextField(p, "location");
        });
    });
    
    intent('What can I do here', p => {
        p.play('Fill out the fields. For example, say "The title is Dentist Appointment."');
    });
    
    //field: title
    intent(textInput("title", "$(TITLE* .+)"), p=> {
        p.TITLE.value = capitalize(p.TITLE.value);
        fillFormField(p, 'title', p.TITLE.value);
        p.play(`The event title is ${p.TITLE.value}`);
        nextField(p, "start");
    });
    visual({"activeField": "title"})(() => {
        intent("title", "$(TITLE* .+)", p=> {
            p.TITLE.value = capitalize(p.TITLE.value);
            fillFormField(p, 'title', p.TITLE.value);
            p.play(`The event title is ${p.TITLE.value}`);
            nextField(p, "start");
        });
    });
    
    //field: start
    intent(datetimeInput("starts on"), p=> {
        const startDateTime = mergeDatetime(p.DATE, p.TIME.time);
        fillFormField(p, 'start', startDateTime);
        p.play(`The event starts at ${p.TIME} on ${sayDate(p.DATE)}`);
        nextField(p, "end");
    });
    intent(textInput("start time", "$(DATE)$(TIME)"), p=> {
        const startDateTime = mergeDatetime(p.DATE, p.TIME.time);
        fillFormField(p, 'start', startDateTime);
        p.play(`The event starts at ${p.TIME} on ${sayDate(p.DATE)}`);
        nextField(p, "end");
    });
    visual({"activeField": "start"})(() => {
        intent("$(DATE) $(TIME)", p=> {
            const startDateTime = mergeDatetime(p.DATE, p.TIME.time);
            fillFormField(p, 'start', startDateTime);
            p.play(`The event starts at ${p.TIME} on ${sayDate(p.DATE)}`);
            nextField(p, "end");
        });
    });
    
    //field: end
    intent(datetimeInput("ends on"), p=> {
        const endDateTime = mergeDatetime(p.DATE, p.TIME.time);
        fillFormField(p, 'end', endDateTime);
        p.play(`The event ends at ${p.TIME} on ${sayDate(p.DATE)}`);
        nextField(p, "tz");
    });
    intent(textInput("end time", "$(DATE)$(TIME)"), p=> {
        const endDateTime = mergeDatetime(p.DATE, p.TIME.time);
        fillFormField(p, 'end', endDateTime);
        p.play(`The event ends at ${p.TIME} on ${sayDate(p.DATE)}`);
        nextField(p, "tz");
    });
    visual({"activeField": "end"})(() => {
        intent("$(DATE) $(TIME)", p=> {
            const endDateTime = mergeDatetime(p.DATE, p.TIME.time);
            fillFormField(p, 'end', endDateTime);
            p.play(`The event ends at ${p.TIME} on ${sayDate(p.DATE)}`);
            nextField(p, "tz");
        });
    });
    
    //field: tz
    intent(textInput("time zone", timezones), p=> {
        fillFormField(p, 'tz', p.TZ.label);
        p.play(`The time zone is ${p.TZ.value}`);
        nextField(p, "freq");
    });
    visual({"activeField": "tz"})(() => {
        intent(timezones, p=> {
            fillFormField(p, 'tz', p.TZ.label);
            p.play(`The time zone is ${p.TZ.value}`);
            nextField(p, "freq");
        });
    });
    
    //field: freq
    intent("The event repeats $(FREQ daily~DAILY|weekly~WEEKLY|every day~DAILY|every week~WEEKLY)", p=> {
        fillFormField(p, 'freq', p.FREQ.label)
        p.play("When does the event stop repeating?")
        p.then(stopRepeat);
    });
    visual({"activeField": "freq"})(() => {
        intent("$(FREQ daily~DAILY|weekly~WEEKLY|every day~DAILY|every week~WEEKLY)", p=> {
            fillFormField(p, 'freq', p.FREQ.label)
            p.play("When does the event stop repeating?")
            p.then(stopRepeat);
        });
    });
    
    //fields: (freq), until
    intent(dateInput("repeats $(FREQ daily~DAILY|weekly~WEEKLY|every day~DAILY|every week~WEEKLY|) until"), p=> { 
        fillFormField(p, 'until', processUntilDate(p.DATE)) 
        if (p.FREQ.value) {
            fillFormField(p, 'freq', p.FREQ.label)
            p.play(`The event repeats ${p.FREQ.label} until ${sayDate(p.DATE)}`);
        } else {
            p.play(`The event repeats until ${sayDate(p.DATE)}`);
            p.play("Does the event repeat daily or weekly?")
            nextField(p, "freq");
            p.then(dailyOrWeekly);
        }  
    });
    visual({"activeField": "until"})(() => {
        intent("$(DATE)", p=> { 
            fillFormField(p, 'until', processUntilDate(p.DATE)) 
            p.play(`The event repeats until ${sayDate(p.DATE)}`);
            p.play("Does the event repeat daily or weekly?")
            nextField(p, "freq");
            p.then(dailyOrWeekly);
        });
    });
    
    //fields: (freq), count
    intent(countInput("repeats $(FREQ daily~DAILY|weekly~WEEKLY|every day~DAILY|every week~WEEKLY|)"), p=> {
        fillFormField(p, 'count', p.NUMBER.number) 
        if (p.FREQ.value) {
            fillFormField(p, 'freq', p.FREQ.label)
        } else {
            p.play(`The event repeats ${p.NUMBER.number} times`);
            p.play("Does the event repeat daily or weekly?")
            nextField(p, "freq");
            p.then(dailyOrWeekly);
        }
    });
    visual({"activeField": "count"})(() => {
        intent("$(NUMBER)(times|)", p=> {
            fillFormField(p, 'count', p.NUMBER.number) 
            p.play(`The event repeats ${p.NUMBER.number} times`);
            p.play("Does the event repeat daily or weekly?")
            nextField(p, "freq");
            p.then(dailyOrWeekly);
        });
    });
    
    //field: location
    intent(textInput("location", "$(LOC)"), p=> {
        p.play({command: 'fillFormField', field: 'location', value: p.LOC.value});
        p.play(`The event is located at ${p.LOC.value}`);
        nextField(p, "desc");
    });
    visual({"activeField": "location"})(() => {
        intent("$(LOC)", p=> {
            p.play({command: 'fillFormField', field: 'location', value: p.LOC.value});
            p.play(`The event is located at ${p.LOC.value}`);
            nextField(p, "desc");
        });
    });
    
    //field: desc
    intent(textInput("description", "$(DESC* .+)"), p=> {
        fillFormField(p, 'desc', p.DESC.value);
        p.play(`The description is ${p.DESC.value}`);
    });
    visual({"activeField": "desc"})(() => {
        intent("$(DESC* .+)", p=> {
            fillFormField(p, 'desc', p.DESC.value);
            p.play(`The description is ${p.DESC.value}`);
        });
    });
    
    fallback('Sorry, I couldn\'t catch that.', 
             'Please fill out the fields by saying something like "The event starts on August 8th at 11 a.m."')
});
