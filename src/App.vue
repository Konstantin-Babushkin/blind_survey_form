<template>
  <SurveyComponent :model="survey" />
  <button @click="scrollToTop" v-show="showButton" class="scroll-to-top-button">
    &#8593;
  </button>
</template>
<script setup lang="ts">
    import { Model } from "survey-core";
    import { SurveyComponent } from "survey-vue3-ui";
    import {computed, ref, watch, onMounted, onUnmounted} from "vue";
    import { useRoute } from "vue-router";
    import 'survey-core/survey-core.css';

    const route = useRoute();
    const id = computed(() => route.query.id)
    const survey = ref();
    const showButton = ref(false);

    const handleScroll = () => {
      showButton.value = window.scrollY > 200;
    };

    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
    };

    onMounted(() => {
      window.addEventListener("scroll", handleScroll);
    });

    onUnmounted(() => {
      window.removeEventListener("scroll", handleScroll);
    });

    watch(id, async (newId) => {
      if (newId) {
        const data = await import(`./tasks/${newId}.json`);
        survey.value = new Model(data.default);
        survey.value.onComplete.add((sender, _) => {
            console.log(JSON.stringify(sender.data, null, 3));
        });
      }
    }, { immediate: true });
</script>

<style scoped>
.scroll-to-top-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.scroll-to-top-button:hover {
  background-color: #0056b3;
}
</style>