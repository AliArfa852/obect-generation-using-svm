import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from keras.datasets import cifar10
from keras.applications import ResNet50
from keras.applications.resnet import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.models import Model
import tensorflow as tf

# Ensure TensorFlow uses the GPU
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Restrict TensorFlow to only allocate memory as needed
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# 1. Load CIFAR-10 dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
y_train = y_train.flatten()
y_test = y_test.flatten()

# 2. Load ResNet50 model pre-trained on ImageNet
resnet = ResNet50(weights="imagenet", include_top=False, input_shape=(32, 32, 3))
feature_extractor = Model(inputs=resnet.input, outputs=resnet.layers[-1].output)

# 3. Extract features using ResNet50
def extract_features(images):
    images = preprocess_input(images)  # Preprocess input for ResNet50
    features = feature_extractor.predict(images)  # Uses GPU if available
    return features.reshape(features.shape[0], -1)  # Flatten the features

x_train_features = extract_features(x_train)
x_test_features = extract_features(x_test)

# 4. Train SVM model
svm_model = SVC(kernel='rbf', C=1, gamma='auto')
svm_model.fit(x_train_features, y_train)

# 5. Make predictions and evaluate
y_pred = svm_model.predict(x_test_features)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 6. Confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
plt.imshow(conf_matrix, cmap="Blues", interpolation="none")
plt.title("Confusion Matrix")
plt.colorbar()
plt.show()

# 7. Visualize predictions
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
def plot_predictions(images, true_labels, pred_labels, class_names, n=10):
    plt.figure(figsize=(15, 5))
    for i in range(n):
        plt.subplot(2, 5, i + 1)
        plt.imshow(images[i])
        plt.title(f"True: {class_names[true_labels[i]]}\nPred: {class_names[pred_labels[i]]}")
        plt.axis('off')

plot_predictions(x_test[:10], y_test[:10], y_pred[:10], class_names)
