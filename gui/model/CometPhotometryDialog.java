/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.util.Optional;
import javafx.application.Platform;
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
    private double window_pos_x=-1;
    private double window_pos_y=-1;
    
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
            
            dialog.setOnCloseRequest(ev -> {
                window_pos_x = dialog.getX();
                window_pos_y = dialog.getY();
            });
            
            dialog.setOnShowing(ev -> {
                if (window_pos_x >= 0 && window_pos_y >= 0) {
                    Platform.runLater(new Runnable() {
                        @Override
                        public void run() {
                            dialog.setX(window_pos_x);
                            dialog.setY(window_pos_y);
                        }
                    });
                }
            });
            
            dialog.setOnShown(ev -> {
                System.out.println("# dialog.setOnShown");
                if (window_pos_x >= 0) dialog.setX(window_pos_x);
                if (window_pos_y >= 0) dialog.setY(window_pos_y);
            });
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
    
    public void setImageSet(ImageSet imageSet) {
        this.imageSet = imageSet;
        /* should be overwritten, if the imageSet has changed we sould call
        setDefaultValues() otherwise resetValues() */
    }
    
    public Optional<ButtonType> run() {
        // set focus on apply button
        dialog.getDialogPane().lookupButton(ButtonType.APPLY).requestFocus();
        return dialog.showAndWait();
    }

}
