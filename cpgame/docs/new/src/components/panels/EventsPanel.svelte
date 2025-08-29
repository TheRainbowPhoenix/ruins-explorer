<script>
    import { events, selectedEvent, selectedPosition, actions, isEventEditorOpen } from '../../store.js';
    import EventEditorDialog from '../dialogs/EventEditorDialog.svelte';

    function addEvent() {
        // Prevent adding an event on top of an existing one
        const posKey = `${$selectedPosition.x},${$selectedPosition.y}`;
        if (!$events[posKey]) {
            actions.addEvent($selectedPosition.x, $selectedPosition.y);
        }
    }

    function editEvent() {
        if ($selectedEvent) {
            isEventEditorOpen.set(true);
        }
    }

    function removeEvent() {
        if ($selectedEvent) {
            actions.removeEvent($selectedEvent.x, $selectedEvent.y);
        }
    }

    function selectEvent(event) {
        selectedEvent.set(event);
        selectedPosition.set({ x: event.x, y: event.y });
    }

    $: eventList = Object.values($events);
    $: canAddEvent = $events[`${$selectedPosition.x},${$selectedPosition.y}`] === undefined;

</script>

{#if $isEventEditorOpen && $selectedEvent}
    <EventEditorDialog event={$selectedEvent} />
{/if}

<div class="form-group">
    <label class="form-label">Event List</label>
    <div class="event-list">
        {#each eventList as event (event.id)}
            <div 
                class="event-item" 
                class:active={$selectedEvent && $selectedEvent.id === event.id}
                on:click={() => selectEvent(event)}
                on:dblclick={editEvent}
            >
                <div><strong>{event.name}</strong></div>
                <div>Position: {event.x}, {event.y}</div>
            </div>
        {/each}
    </div>
</div>

<div class="form-group">
    <button class="btn btn-primary" on:click={addEvent} disabled={!canAddEvent}>Add Event Here</button>
    <button class="btn btn-secondary" disabled={!$selectedEvent} on:click={editEvent}>
        Edit Event
    </button>
    <button class="btn btn-danger" disabled={!$selectedEvent} on:click={removeEvent}>
        Remove Event
    </button>
</div>