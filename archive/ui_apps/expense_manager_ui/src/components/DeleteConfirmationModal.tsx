import React from 'react';
import './Modal.css';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  itemName: string; // e.g., "this entry"
}

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({ isOpen, onClose, onConfirm, itemName }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content confirmation-modal-content">
        <div className="modal-header">
          <h2>Confirm Deletion</h2>
        </div>
        <p>Are you sure you want to delete {itemName}?</p>
        <div className="modal-actions confirmation-modal-actions">
          <button type="button" className="modal-button secondary" onClick={onClose}>
            Cancel
          </button>
          <button type="button" className="modal-button primary" onClick={onConfirm}>
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal;
