<script>
    import { events, selectedEvent, selectedPosition, actions } from '../../store.js';

    function addEvent() {
        actions.addEvent($selectedPosition.x, $selectedPosition.y);
    }

    function editEvent() {
        if ($selectedEvent) {
            showEventEditorDialog();
        }
    }

    function removeEvent() {
        actions.removeEvent($selectedPosition.x, $selectedPosition.y);
    }

    function selectEvent(event) {
        selectedEvent.set(event);
        selectedPosition.set({ x: event.x, y: event.y });
    }

    function showEventEditorDialog() {
        // This would open a modal dialog - placeholder for now
        console.log('Event editor dialog would open here');
    }

    $: eventList = Object.keys($events).map(posKey => {
        const [x, y] = posKey.split(',').map(Number);
        return { ...($events)[posKey], posKey };
    });
</script>

<div class="form-group">
    <label class="form-label">Event List</label>
    <div class="event-list">
        {#each eventList as event}
            <div 
                class="event-item" 
                class:active={$selectedPosition.x === event.x && $selectedPosition.y === event.y}
                on:click={() => selectEvent(event)}
            >
                <div><strong>{event.name}</strong></div>
                <div>Position: {event.x}, {event.y}</div>
            </div>
        {/each}
    </div>
</div>

<div class="form-group">
    <button class="btn btn-primary" on:click={addEvent}>Add Event</button>
    <button 
        class="btn btn-secondary" 
        disabled={!$selectedEvent}
        on:click={editEvent}
    >
        Edit Event
    </button>
    <button 
        class="btn btn-danger" 
        disabled={!$selectedEvent}
        on:click={removeEvent}
    >
        Remove Event
    </button>
</div>