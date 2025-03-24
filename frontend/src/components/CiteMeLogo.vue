<script setup >
import { ref, onMounted } from 'vue';

const logoRotation = ref(0);

onMounted(() => {
  // Gentle rotation animation for the 3D effect
  setInterval(() => {
    logoRotation.value = (logoRotation.value + 1) % 360;
  }, 100);
});
</script>

<template>
  <div class="logo-container">
    <!-- Main Logo -->
    <div class="logo" :style="{ transform: `rotateY(${logoRotation}deg)` }">
      <div class="book-stack">
        <div class="book book1"></div>
        <div class="book book2"></div>
        <div class="book book3"></div>
      </div>
      <div class="quote-mark">"</div>
    </div>
  </div>
</template>

<style scoped>
.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 24px;
  width: 24px;
}

.logo {
  position: relative;
  width: 24px;
  height: 24px;
  perspective: 1000px;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
}

.book-stack {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
}

.book {
  position: absolute;
  width: 16px;
  height: 20px;
  border-radius: 2px;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.book1 {
  transform: translateZ(4px) rotate(-15deg);
  background: linear-gradient(135deg, #4a90e2, #357abd);
}

.book2 {
  transform: translateZ(2px) rotate(-5deg);
  background: linear-gradient(135deg, #5c6bc0, #3f51b5);
}

.book3 {
  transform: translateZ(0) rotate(5deg);
  background: linear-gradient(135deg, #7e57c2, #5e35b1);
}

.quote-mark {
  position: absolute;
  top: 50%;
  left: 30%;
  transform: translate(-50%, -50%) translateZ(6px);
  font-size: 14px;
  font-weight: bold;
  color: #ffffff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.favicon-preview {
  text-align: center;
}

.favicon-preview p {
  margin-bottom: 1rem;
  color: #666;
}

.favicon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: linear-gradient(135deg, #4a90e2, #7e57c2);
  position: relative;
  margin: 0 auto;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.favicon::after {
  content: '"';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 24px;
  font-weight: bold;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Add responsive design */
@media (max-width: 768px) {
  .logo-container {
    height: 20px;
    width: 20px;
  }

  .logo {
    width: 20px;
    height: 20px;
  }
}
</style>
