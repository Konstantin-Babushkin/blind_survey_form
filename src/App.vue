<template>
  <div v-if="survey">
    <SurveyComponent :model="survey" />
  </div>
  <div v-else>
    <p>Загрузка опроса...</p>
  </div>
  <button @click="scrollToTop" v-show="showButton" class="scroll-to-top-button">
    &#8593;
  </button>
</template>
<script setup lang="ts">
    import { Model } from "survey-core";
    import { SurveyComponent } from "survey-vue3-ui";
    import {computed, ref, watch, onMounted, onUnmounted} from "vue";
    import { useRoute } from "vue-router";

    const route = useRoute();
    const id = computed(() => route.query.id || 'a1') // по умолчанию загружаем a1
    const survey = ref<Model | null>(null);
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
        try {
          const data = await import(`./tasks/${newId}.json`);
          const surveyModel = new Model(data.default);
          surveyModel.onComplete.add((sender, _) => {
              console.log(JSON.stringify(sender.data, null, 3));
          });
          survey.value = surveyModel;
        } catch (error) {
          console.error(`Ошибка загрузки опроса ${newId}:`, error);
        }
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