"""
CNN-based Piece Classifier
Neural network for chess piece recognition from square images
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
import numpy as np
from typing import Tuple, Optional, List, Dict
import os


class ChessPieceDataset(Dataset):
    """Dataset for chess piece images"""
    
    # Piece classes: 0=empty, 1-6=white pieces (P,N,B,R,Q,K), 7-12=black pieces (p,n,b,r,q,k)
    PIECE_CLASSES = ['empty', 'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    NUM_CLASSES = 13
    
    def __init__(self, image_dir: str, labels_file: str, transform: Optional[transforms.Compose] = None):
        """
        Initialize dataset
        
        Args:
            image_dir: Directory containing square images
            labels_file: File with image labels (format: "image_name.png label")
            transform: Optional image transforms
        """
        self.image_dir = image_dir
        self.transform = transform or self._default_transform()
        self.images = []
        self.labels = []
        
        if os.path.exists(labels_file):
            with open(labels_file, 'r') as f:
                for line in f:
                    img_name, label = line.strip().split()
                    self.images.append(img_name)
                    self.labels.append(int(label))
    
    def _default_transform(self) -> transforms.Compose:
        """Get default image transforms"""
        return transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
    
    def __len__(self) -> int:
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Tuple:
        # This is a placeholder - implement actual image loading as needed
        return torch.zeros(3, 64, 64), torch.tensor(self.labels[idx])


class ChessPieceCNN(nn.Module):
    """Convolutional Neural Network for chess piece classification"""
    
    def __init__(self, num_classes: int = 13, pretrained: bool = True):
        """
        Initialize CNN model
        
        Args:
            num_classes: Number of output classes (13 for chess pieces)
            pretrained: Whether to use ImageNet pretrained weights
        """
        super(ChessPieceCNN, self).__init__()
        
        # Load pretrained ResNet18
        self.backbone = models.resnet18(pretrained=pretrained)
        
        # Modify final layer for chess pieces
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
        
        self.num_classes = num_classes
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.backbone(x)
    
    def forward_with_confidence(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass with confidence scores
        
        Args:
            x: Input tensor
            
        Returns:
            Tuple of (logits, probabilities)
        """
        logits = self.forward(x)
        probabilities = torch.softmax(logits, dim=1)
        return logits, probabilities


class PieceClassifier:
    """Wrapper for chess piece classification"""
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize piece classifier
        
        Args:
            model_path: Path to saved model weights
            device: Device to run model on (cuda/cpu)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ChessPieceCNN(num_classes=13, pretrained=True)
        self.model = self.model.to(self.device)
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
    
    def classify_squares(self, squares: np.ndarray) -> Dict:
        """
        Classify all squares in a chess board
        
        Args:
            squares: Array of shape (8, 8, 64, 64, 3) containing square images
            
        Returns:
            Dictionary with classifications and confidences
        """
        predictions = []
        confidences = []
        
        with torch.no_grad():
            for i in range(8):
                row_predictions = []
                row_confidences = []
                
                for j in range(8):
                    square_img = squares[i, j]
                    
                    # Convert to tensor if needed
                    if isinstance(square_img, np.ndarray):
                        from PIL import Image
                        square_img = Image.fromarray(square_img.astype('uint8'))
                    
                    # Apply transform
                    square_tensor = self.transform(square_img).unsqueeze(0).to(self.device)
                    
                    # Get prediction
                    logits, probs = self.model.forward_with_confidence(square_tensor)
                    pred_class = torch.argmax(probs, dim=1).item()
                    confidence = torch.max(probs).item()
                    
                    row_predictions.append(pred_class)
                    row_confidences.append(confidence)
                
                predictions.append(row_predictions)
                confidences.append(row_confidences)
        
        return {
            "predictions": np.array(predictions),
            "confidences": np.array(confidences),
            "board_matrix": self._predictions_to_board(predictions)
        }
    
    def classify_single_square(self, square_img: np.ndarray) -> Dict:
        """
        Classify a single square
        
        Args:
            square_img: Square image (preferably 64x64)
            
        Returns:
            Dictionary with classification and confidence
        """
        with torch.no_grad():
            from PIL import Image
            if isinstance(square_img, np.ndarray):
                square_img = Image.fromarray(square_img.astype('uint8'))
            
            square_tensor = self.transform(square_img).unsqueeze(0).to(self.device)
            logits, probs = self.model.forward_with_confidence(square_tensor)
            
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = torch.max(probs).item()
            all_probs = probs[0].cpu().numpy()
            
            return {
                "predicted_class": pred_class,
                "predicted_piece": ChessPieceDataset.PIECE_CLASSES[pred_class],
                "confidence": float(confidence),
                "all_probabilities": {
                    piece: float(prob) 
                    for piece, prob in zip(ChessPieceDataset.PIECE_CLASSES, all_probs)
                }
            }
    
    def _predictions_to_board(self, predictions: List[List[int]]) -> List[List[str]]:
        """Convert class predictions to piece symbols"""
        board = []
        for row_pred in predictions:
            row = []
            for pred in row_pred:
                if pred < len(ChessPieceDataset.PIECE_CLASSES):
                    piece = ChessPieceDataset.PIECE_CLASSES[pred]
                    row.append(piece if piece != 'empty' else '')
                else:
                    row.append('')
            board.append(row)
        return board
    
    def save_model(self, model_path: str):
        """Save model weights"""
        torch.save(self.model.state_dict(), model_path)
    
    def load_model(self, model_path: str):
        """Load model weights"""
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
    
    def train_mode(self):
        """Set model to training mode"""
        self.model.train()
    
    def eval_mode(self):
        """Set model to evaluation mode"""
        self.model.eval()


class TrainChessCNN:
    """Training utility for chess piece CNN"""
    
    def __init__(self, model_path: str = "chess_cnn_model.pth", device: Optional[str] = None):
        """
        Initialize trainer
        
        Args:
            model_path: Path to save model
            device: Device to train on
        """
        self.model_path = model_path
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ChessPieceCNN(num_classes=13, pretrained=True)
        self.model = self.model.to(self.device)
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-4)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train one epoch"""
        self.model.train()
        total_loss = 0
        
        for images, labels in train_loader:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """Validate model"""
        self.model.eval()
        correct = 0
        total = 0
        total_loss = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        avg_loss = total_loss / len(val_loader)
        return accuracy, avg_loss
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
             epochs: int = 50, save_best: bool = True):
        """Train model"""
        best_accuracy = 0
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_accuracy, val_loss = self.validate(val_loader)
            self.scheduler.step()
            
            if (epoch + 1) % 5 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], '
                      f'Train Loss: {train_loss:.4f}, '
                      f'Val Loss: {val_loss:.4f}, '
                      f'Val Accuracy: {val_accuracy:.2f}%')
            
            if save_best and val_accuracy > best_accuracy:
                best_accuracy = val_accuracy
                self.model.eval()
                torch.save(self.model.state_dict(), self.model_path)
                print(f'Best model saved with accuracy: {best_accuracy:.2f}%')


if __name__ == "__main__":
    # Test the model
    print("Chess Piece CNN Module")
    print(f"Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    print(f"Piece classes: {ChessPieceDataset.PIECE_CLASSES}")
    print(f"Number of classes: {ChessPieceDataset.NUM_CLASSES}")
    
    # Create a model instance
    classifier = PieceClassifier()
    print(f"\nModel created and ready on device: {classifier.device}")
