<template>
  <div v-if="survey">
    <SurveyComponent :model="survey as any" />
  </div>
  <div v-else>
    <p>Loading...</p>
  </div>
  <button @click="scrollToTop" v-show="showButton" class="scroll-to-top-button">
    &#8593;
  </button>
</template>
<script setup lang="ts">
    import { Model } from "survey-core";
    import { SurveyComponent } from "survey-vue3-ui";
    import {computed, ref, watch, onMounted, onUnmounted} from "vue";
    import { useRoute, useRouter } from "vue-router";
    import { db } from "./firebase";
    import { collection, addDoc, serverTimestamp } from "firebase/firestore";

    const route = useRoute();
    const router = useRouter();
    const id = computed(() => route.query.id || 'a1')
    const survey = ref<Model | null>(null);
    const showButton = ref(false);

    const saveSurveyResults = async (surveyData: any, taskId: string) => {
      try {
        const docRef = await addDoc(collection(db, "survey_results"), {
          taskId: taskId,
          responses: surveyData,
          timestamp: serverTimestamp(),
          userAgent: navigator.userAgent,
          url: window.location.href
        });

        console.log("✅ Results saved to Firebase with ID:", docRef.id);
        console.log("📊 Survey data:", JSON.stringify(surveyData, null, 3));

        alert("Thank you! Your answers have been saved successfully.");

      } catch (error) {
        console.error("❌ Error saving to Firebase:", error);
        console.log("📊 Survey data (NOT saved):", JSON.stringify(surveyData, null, 3));
        alert("An error occurred while saving. Please notify the administrator.");
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

          const pageFromUrl = route.query.page;
          if (pageFromUrl && !isNaN(parseInt(pageFromUrl as string))) {
            surveyModel.currentPageNo = parseInt(pageFromUrl as string);
          }

          surveyModel.onCurrentPageChanged.add((sender, _) => {
            const newPage = sender.currentPageNo;
            if (String(newPage) !== route.query.page) {
              router.replace({ query: { ...route.query, page: newPage } });
            }
          });

          surveyModel.onComplete.add((sender, _) => {
              saveSurveyResults(sender.data, newId as string);
              const { page, ...query } = route.query;
              router.replace({ query });
          });
          survey.value = surveyModel;
        } catch (error) {
          console.error(`Error loading survey ${newId}:`, error);
        }
      }
    }, { immediate: true });

    watch(() => route.query.page, (newPageStr) => {
      if (survey.value) {
        const newPage = newPageStr ? parseInt(newPageStr as string, 10) : 0;
        if (!isNaN(newPage) && survey.value.currentPageNo !== newPage) {
          survey.value.currentPageNo = newPage;
        }
      }
    });
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
