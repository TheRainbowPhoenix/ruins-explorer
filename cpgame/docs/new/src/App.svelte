<script>
    import ActivityBar from './components/ActivityBar.svelte';
    import Sidebar from './components/Sidebar.svelte';
    import MainContent from './components/MainContent.svelte';
    import Tooltip from './components/Tooltip.svelte';
</script>

<div class="workbench">
    <ActivityBar />
    <Sidebar />
    <MainContent />
</div>

<Tooltip />