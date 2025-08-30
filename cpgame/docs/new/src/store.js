import { writable, derived, get } from 'svelte/store';

// Create stores for editor state
export const currentPanel = writable('map');
export const currentTool = writable('place');
export const selectedTile = writable(0);
export const zoomLevel = writable(1);
export const mapWidth = writable(14);
export const mapHeight = writable(10);
export const tileSize = writable(20);
export const displayName = writable("Quiet Village");
export const tilesetId = writable("jrpg");
export const scrollType = writable(0);
export const specifyBattleback = writable(false);

// Map data - initialize with all 0s
export const mapData = writable(Array(14 * 10).fill(0));
export const events = writable({});
export const selectedEvent = writable(null);
export const selectedPosition = writable({ x: 0, y: 0 });
export const isDrawing = writable(false);
export const areaStart = writable(null);
export const areaEnd = writable(null);
export const hoveredTile = writable(null);
export const lastHoveredTile = writable(null);
export const lastSelectedPosition = writable({ x: -1, y: -1 });

// Guide Line State
export const guidesEnabled = writable(false);
export const guidePageWidth = writable(16);
export const guidePageHeight = writable(24);
export const isGuideEditorOpen = writable(false);

// Dialog and Tooltip State
export const isEventEditorOpen = writable(false);
export const tooltip = writable({ visible: false, content: '', x: 0, y: 0 });


// Derived stores
export const editorMode = derived(currentTool, ($currentTool) => 
    $currentTool.charAt(0).toUpperCase() + $currentTool.slice(1)
);

export const canvasSize = derived(
    [mapWidth, mapHeight, tileSize, zoomLevel],
    ([$mapWidth, $mapHeight, $tileSize, $zoomLevel]) => ({
        width: $mapWidth * $tileSize * $zoomLevel,
        height: $mapHeight * $tileSize * $zoomLevel
    })
);

// Actions
export const actions = {
    resizeMap(newWidth, newHeight) {
        const oldWidth = get(mapWidth);
        const oldHeight = get(mapHeight);
        const oldData = get(mapData);

        const newData = Array(newWidth * newHeight).fill(0);
        
        // Copy old data to new map (crop or expand)
        for (let y = 0; y < Math.min(oldHeight, newHeight); y++) {
            for (let x = 0; x < Math.min(oldWidth, newWidth); x++) {
                const oldIndex = y * oldWidth + x;
                const newIndex = y * newWidth + x;
                newData[newIndex] = oldData[oldIndex];
            }
        }
        
        mapWidth.set(newWidth);
        mapHeight.set(newHeight);
        mapData.set(newData);
        
        // Update events (remove events that are now out of bounds)
        events.update(oldEvents => {
            const newEvents = {};
            Object.keys(oldEvents).forEach(posKey => {
                const [x, y] = posKey.split(',').map(Number);
                if (x < newWidth && y < newHeight) {
                    newEvents[posKey] = oldEvents[posKey];
                }
            });
            return newEvents;
        });
    },

    placeTile(x, y, tileId) {
        mapData.update(data => {
            const width = get(mapWidth);
            const newData = [...data];
            const index = y * width + x;
            if (index >= 0 && index < newData.length) {
                newData[index] = tileId;
            }
            return newData;
        });
    },

    fillMap(tileId) {
        const width = get(mapWidth);
        const height = get(mapHeight);
        mapData.set(Array(width * height).fill(tileId));
    },

    addEvent(x, y) {
        events.update(currentEvents => {
            const posKey = `${x},${y}`;
            if (!currentEvents[posKey]) {
                const newEvent = {
                    id: Object.keys(currentEvents).length + 1,
                    name: `Event ${Object.keys(currentEvents).length + 1}`,
                    x: x,
                    y: y,
                    pages: [{
                        graphic: { tileId: 0 },
                        list: []
                    }]
                };
                currentEvents[posKey] = newEvent;
                selectedEvent.set(newEvent);
            }
            return currentEvents;
        });
    },
    
    updateEvent(eventData) {
        events.update(currentEvents => {
            const posKey = `${eventData.x},${eventData.y}`;
            currentEvents[posKey] = eventData;
            return currentEvents;
        });
        const currentSelected = get(selectedEvent);
        if (currentSelected && currentSelected.id === eventData.id) {
            selectedEvent.set(eventData);
        }
    },

    removeEvent(x, y) {
        events.update(currentEvents => {
            const posKey = `${x},${y}`;
            delete currentEvents[posKey];
            return currentEvents;
        });
        selectedEvent.set(null);
    },

    loadProject(projectData) {
        displayName.set(projectData.displayName || "Untitled");
        tilesetId.set(projectData.tilesetId || "default");
        mapWidth.set(projectData.width || 20);
        mapHeight.set(projectData.height || 15);
        scrollType.set(projectData.scrollType || 0);
        specifyBattleback.set(projectData.specifyBattleback || false);
        mapData.set(projectData.data || Array(projectData.width * projectData.height).fill(0));
        events.set(projectData.events || {});
    }
};