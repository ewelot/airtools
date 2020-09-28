/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.util.Optional;
import javafx.fxml.FXMLLoader;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Dialog;
import javafx.scene.control.DialogPane;
import javafx.stage.Modality;

/**
 *
 * @author lehmann
 */
public class CometPhotometryDialog {
    
    private Dialog dialog;
    private ImageSet imageSet;
    private Object controller;
    
    public CometPhotometryDialog(String fxml, String title) {
        if (dialog == null) try {
            System.out.println("creating dialog for " + title);
            FXMLLoader loader;
            loader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/" + fxml));
            DialogPane pane = (DialogPane) loader.load();
            controller = loader.getController();

            // create dialog
            dialog = new Dialog();
            dialog.setDialogPane((DialogPane) pane);
            dialog.setTitle(title);
            dialog.initModality(Modality.WINDOW_MODAL);
            //dialog.initOwner(pane.getScene().getWindow());

            ((Button) pane.lookupButton(ButtonType.APPLY)).setText("Apply");
            ((Button) pane.lookupButton(ButtonType.CANCEL)).setText("Cancel");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public Object getController() {
        return controller;
    }
    
    public ImageSet getImageSet() {
        return imageSet;
    }
    
    public void setImageSet(ImageSet imgSet) {
        imageSet = imgSet;
        // note: objects must also call controller.setImageSet(imgSet)
    }
    
    public boolean isNewImageSet (ImageSet nextImageSet) {
        boolean isNew=false;
        if (imageSet == null) {
            isNew = true;
        } else {
            isNew = ! nextImageSet.getSetname().equals(imageSet.getSetname());
        }
        // if (isNew) setImageSet(nextImageSet);
        return isNew;
    }

    public Optional<ButtonType> run() {
        // set focus on apply button
        dialog.getDialogPane().lookupButton(ButtonType.APPLY).requestFocus();

        return dialog.showAndWait();
    }

}
