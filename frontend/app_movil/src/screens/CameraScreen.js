/**
 * PANTALLA DE CÁMARA PARA FOTOS DE CULTIVOS
 * Permite tomar fotos de cultivos con geolocalización y metadatos
 */

import React, {useState, useEffect, useRef} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  Modal,
  TextInput,
  ScrollView,
  Dimensions,
} from 'react-native';
import {launchCamera, launchImageLibrary} from 'react-native-image-picker';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

import LocationService from '../services/LocationService';
import ApiService from '../services/ApiService';
import StorageService from '../services/StorageService';

const {width: screenWidth, height: screenHeight} = Dimensions.get('window');

const COLORS = {
  primary: '#2E7D32',
  secondary: '#4CAF50',
  accent: '#FF9800',
  background: '#F5F5F5',
  surface: '#FFFFFF',
  text: '#212121',
  textSecondary: '#757575',
  error: '#F44336',
  warning: '#FF9800',
  success: '#4CAF50',
  info: '#2196F3',
};

const CameraScreen = ({navigation}) => {
  const [photos, setPhotos] = useState([]);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [cropType, setCropType] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    loadPhotos();
    getCurrentLocation();
  }, []);

  const loadPhotos = async () => {
    try {
      const savedPhotos = await StorageService.getPhotos();
      setPhotos(savedPhotos || []);
    } catch (error) {
      console.error('[CAMERA] Error cargando fotos:', error);
    }
  };

  const getCurrentLocation = async () => {
    try {
      const location = await LocationService.getCurrentLocation();
      setCurrentLocation(location);
    } catch (error) {
      console.error('[CAMERA] Error obteniendo ubicación:', error);
      Alert.alert('Ubicación', 'No se pudo obtener la ubicación actual');
    }
  };

  const takePhoto = () => {
    const options = {
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1920,
      maxHeight: 1920,
      includeBase64: false,
    };

    launchCamera(options, handleImageResponse);
  };

  const selectFromGallery = () => {
    const options = {
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1920,
      maxHeight: 1920,
      includeBase64: false,
    };

    launchImageLibrary(options, handleImageResponse);
  };

  const handleImageResponse = (response) => {
    if (response.didCancel || response.error) {
      return;
    }

    if (response.assets && response.assets.length > 0) {
      const asset = response.assets[0];
      
      const photoData = {
        id: Date.now().toString(),
        uri: asset.uri,
        width: asset.width,
        height: asset.height,
        fileSize: asset.fileSize,
        timestamp: new Date(),
        location: currentLocation,
        cropType: '',
        notes: '',
        synced: false,
      };

      setSelectedPhoto(photoData);
      setModalVisible(true);
    }
  };

  const savePhoto = async () => {
    if (!selectedPhoto || !cropType.trim()) {
      Alert.alert('Error', 'Por favor, seleccione un tipo de cultivo');
      return;
    }

    try {
      setLoading(true);

      const photoToSave = {
        ...selectedPhoto,
        cropType: cropType.trim(),
        notes: notes.trim(),
      };

      // Guardar foto localmente
      await StorageService.savePhoto(photoToSave);

      // Sincronizar con servidor si hay conexión
      try {
        await ApiService.uploadPhoto(photoToSave);
        photoToSave.synced = true;
        await StorageService.updatePhoto(photoToSave);
      } catch (syncError) {
        console.log('[CAMERA] Foto guardada localmente, se sincronizará después');
      }

      // Actualizar lista de fotos
      setPhotos(prev => [photoToSave, ...prev]);

      // Limpiar formulario
      setSelectedPhoto(null);
      setCropType('');
      setNotes('');
      setModalVisible(false);

      Alert.alert('Éxito', 'Foto guardada correctamente');

    } catch (error) {
      console.error('[CAMERA] Error guardando foto:', error);
      Alert.alert('Error', 'No se pudo guardar la foto');
    } finally {
      setLoading(false);
    }
  };

  const deletePhoto = async (photoId) => {
    Alert.alert(
      'Eliminar Foto',
      '¿Está seguro de que desea eliminar esta foto?',
      [
        {text: 'Cancelar', style: 'cancel'},
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            try {
              await StorageService.deletePhoto(photoId);
              setPhotos(prev => prev.filter(photo => photo.id !== photoId));
              Alert.alert('Éxito', 'Foto eliminada correctamente');
            } catch (error) {
              console.error('[CAMERA] Error eliminando foto:', error);
              Alert.alert('Error', 'No se pudo eliminar la foto');
            }
          },
        },
      ]
    );
  };

  const syncPhoto = async (photo) => {
    try {
      setLoading(true);
      await ApiService.uploadPhoto(photo);
      
      const updatedPhoto = {...photo, synced: true};
      await StorageService.updatePhoto(updatedPhoto);
      
      setPhotos(prev => 
        prev.map(p => p.id === photo.id ? updatedPhoto : p)
      );
      
      Alert.alert('Éxito', 'Foto sincronizada correctamente');
    } catch (error) {
      console.error('[CAMERA] Error sincronizando foto:', error);
      Alert.alert('Error', 'No se pudo sincronizar la foto');
    } finally {
      setLoading(false);
    }
  };

  const renderPhotoItem = (photo) => (
    <View key={photo.id} style={styles.photoItem}>
      <Image source={{uri: photo.uri}} style={styles.photoThumbnail} />
      
      <View style={styles.photoInfo}>
        <Text style={styles.photoCrop}>{photo.cropType}</Text>
        <Text style={styles.photoDate}>
          {new Date(photo.timestamp).toLocaleDateString()}
        </Text>
        
        {photo.location && (
          <Text style={styles.photoLocation}>
            📍 {photo.location.latitude.toFixed(4)}, {photo.location.longitude.toFixed(4)}
          </Text>
        )}
        
        {photo.notes && (
          <Text style={styles.photoNotes} numberOfLines={2}>
            {photo.notes}
          </Text>
        )}
        
        <View style={styles.photoActions}>
          {!photo.synced && (
            <TouchableOpacity
              style={styles.syncButton}
              onPress={() => syncPhoto(photo)}
              disabled={loading}
            >
              <Icon name="cloud-upload" size={16} color={COLORS.info} />
              <Text style={styles.syncButtonText}>Sincronizar</Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => deletePhoto(photo.id)}
          >
            <Icon name="delete" size={16} color={COLORS.error} />
            <Text style={styles.deleteButtonText}>Eliminar</Text>
          </TouchableOpacity>
        </View>
        
        {photo.synced && (
          <View style={styles.syncedIndicator}>
            <Icon name="cloud-done" size={16} color={COLORS.success} />
            <Text style={styles.syncedText}>Sincronizado</Text>
          </View>
        )}
      </View>
    </View>
  );

  const cropTypes = [
    'Palto',
    'Uva',
    'Cítricos',
    'Hortalizas',
    'Cereales',
    'Otros',
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Fotos de Cultivos</Text>
        <Text style={styles.headerSubtitle}>
          {photos.length} fotos guardadas
        </Text>
      </View>

      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.cameraButton} onPress={takePhoto}>
          <LinearGradient
            colors={[COLORS.primary, COLORS.secondary]}
            style={styles.buttonGradient}
          >
            <Icon name="camera-alt" size={24} color={COLORS.surface} />
            <Text style={styles.buttonText}>Tomar Foto</Text>
          </LinearGradient>
        </TouchableOpacity>

        <TouchableOpacity style={styles.galleryButton} onPress={selectFromGallery}>
          <LinearGradient
            colors={[COLORS.accent, '#FFB74D']}
            style={styles.buttonGradient}
          >
            <Icon name="photo-library" size={24} color={COLORS.surface} />
            <Text style={styles.buttonText}>Galería</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>

      {currentLocation && (
        <View style={styles.locationInfo}>
          <Icon name="location-on" size={16} color={COLORS.success} />
          <Text style={styles.locationText}>
            Ubicación: {currentLocation.latitude.toFixed(4)}, {currentLocation.longitude.toFixed(4)}
          </Text>
        </View>
      )}

      <ScrollView style={styles.photosContainer}>
        {photos.length > 0 ? (
          photos.map(renderPhotoItem)
        ) : (
          <View style={styles.emptyState}>
            <Icon name="photo-camera" size={64} color={COLORS.textSecondary} />
            <Text style={styles.emptyStateText}>
              No hay fotos guardadas
            </Text>
            <Text style={styles.emptyStateSubtext}>
              Tome su primera foto de cultivo
            </Text>
          </View>
        )}
      </ScrollView>

      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Información de la Foto</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Icon name="close" size={24} color={COLORS.text} />
              </TouchableOpacity>
            </View>

            {selectedPhoto && (
              <Image source={{uri: selectedPhoto.uri}} style={styles.modalImage} />
            )}

            <ScrollView style={styles.modalForm}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Tipo de Cultivo *</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  <View style={styles.cropTypeContainer}>
                    {cropTypes.map((type) => (
                      <TouchableOpacity
                        key={type}
                        style={[
                          styles.cropTypeButton,
                          cropType === type && styles.cropTypeButtonSelected,
                        ]}
                        onPress={() => setCropType(type)}
                      >
                        <Text
                          style={[
                            styles.cropTypeText,
                            cropType === type && styles.cropTypeTextSelected,
                          ]}
                        >
                          {type}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </ScrollView>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Notas (opcional)</Text>
                <TextInput
                  style={styles.textInput}
                  value={notes}
                  onChangeText={setNotes}
                  placeholder="Agregar notas sobre el cultivo..."
                  multiline
                  numberOfLines={3}
                />
              </View>

              {selectedPhoto?.location && (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Ubicación</Text>
                  <Text style={styles.locationInfo}>
                    📍 {selectedPhoto.location.latitude.toFixed(6)}, {selectedPhoto.location.longitude.toFixed(6)}
                  </Text>
                </View>
              )}
            </ScrollView>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.saveButton}
                onPress={savePhoto}
                disabled={loading}
              >
                <LinearGradient
                  colors={[COLORS.primary, COLORS.secondary]}
                  style={styles.buttonGradient}
                >
                  <Text style={styles.saveButtonText}>
                    {loading ? 'Guardando...' : 'Guardar'}
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    padding: 20,
    backgroundColor: COLORS.surface,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginTop: 5,
  },
  actionButtons: {
    flexDirection: 'row',
    padding: 20,
    justifyContent: 'space-around',
  },
  cameraButton: {
    flex: 1,
    marginRight: 10,
  },
  galleryButton: {
    flex: 1,
    marginLeft: 10,
  },
  buttonGradient: {
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  buttonText: {
    color: COLORS.surface,
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: COLORS.surface,
    marginHorizontal: 20,
    borderRadius: 8,
    marginBottom: 10,
  },
  locationText: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginLeft: 5,
  },
  photosContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  photoItem: {
    flexDirection: 'row',
    backgroundColor: COLORS.surface,
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  photoThumbnail: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 15,
  },
  photoInfo: {
    flex: 1,
  },
  photoCrop: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 5,
  },
  photoDate: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 5,
  },
  photoLocation: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 5,
  },
  photoNotes: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 10,
  },
  photoActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  syncButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 5,
    backgroundColor: '#E3F2FD',
  },
  syncButtonText: {
    fontSize: 12,
    color: COLORS.info,
    marginLeft: 5,
  },
  deleteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 5,
    backgroundColor: '#FFEBEE',
  },
  deleteButtonText: {
    fontSize: 12,
    color: COLORS.error,
    marginLeft: 5,
  },
  syncedIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
  },
  syncedText: {
    fontSize: 12,
    color: COLORS.success,
    marginLeft: 5,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 50,
  },
  emptyStateText: {
    fontSize: 18,
    color: COLORS.textSecondary,
    marginTop: 15,
    textAlign: 'center',
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 5,
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: COLORS.surface,
    margin: 20,
    borderRadius: 10,
    maxHeight: screenHeight * 0.8,
    width: screenWidth - 40,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  modalImage: {
    width: '100%',
    height: 200,
    resizeMode: 'cover',
  },
  modalForm: {
    padding: 20,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 10,
  },
  cropTypeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  cropTypeButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F5F5F5',
    marginRight: 10,
    marginBottom: 10,
  },
  cropTypeButtonSelected: {
    backgroundColor: COLORS.primary,
  },
  cropTypeText: {
    fontSize: 14,
    color: COLORS.text,
  },
  cropTypeTextSelected: {
    color: COLORS.surface,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    color: COLORS.text,
    textAlignVertical: 'top',
  },
  modalActions: {
    flexDirection: 'row',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  cancelButton: {
    flex: 1,
    padding: 15,
    alignItems: 'center',
    marginRight: 10,
  },
  cancelButtonText: {
    fontSize: 16,
    color: COLORS.textSecondary,
  },
  saveButton: {
    flex: 1,
    marginLeft: 10,
  },
  saveButtonText: {
    color: COLORS.surface,
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default CameraScreen;



