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
    import { db } from "./firebase";
    import { collection, addDoc, serverTimestamp } from "firebase/firestore";

    const route = useRoute();
    const id = computed(() => route.query.id || 'a1') // по умолчанию загружаем a1
    const survey = ref<Model | null>(null);
    const showButton = ref(false);

    // Функция для сохранения результатов в Firebase
    const saveSurveyResults = async (surveyData: any, taskId: string) => {
      try {
        const docRef = await addDoc(collection(db, "survey_results"), {
          taskId: taskId,
          responses: surveyData,
          timestamp: serverTimestamp(),
          userAgent: navigator.userAgent,
          url: window.location.href
        });
        
        console.log("✅ Результаты сохранены в Firebase с ID:", docRef.id);
        console.log("📊 Данные опроса:", JSON.stringify(surveyData, null, 3));
        
        // Показываем уведомление пользователю
        alert("Спасибо! Ваши ответы успешно сохранены.");
        
      } catch (error) {
        console.error("❌ Ошибка сохранения в Firebase:", error);
        console.log("📊 Данные опроса (НЕ сохранены):", JSON.stringify(surveyData, null, 3));
        alert("Произошла ошибка при сохранении. Пожалуйста, сообщите администратору.");
      }
    };

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
              saveSurveyResults(sender.data, newId);
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