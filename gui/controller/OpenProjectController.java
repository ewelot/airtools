/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.util.Properties;
import java.util.ResourceBundle;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class OpenProjectController implements Initializable {

    @FXML
    private AnchorPane paneOpenProject;
    @FXML
    private TextField tfProjectDir;
    @FXML
    private Button buttonBrowseProjectDir;
    
    private StringProperty projectDir = new SimpleStringProperty();

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // Textfields
        tfProjectDir.setText("no project");
        
    }
    
    
    public void setReferences (StringProperty projectDir) {
        this.projectDir=projectDir;
        File f = new File(projectDir.getValue());
        String path=f.getParent();
        if (path.equals("/") || path.equals("/home")) path=f.getPath();
        tfProjectDir.setText(path);
    }
    
        
    @FXML
    private void handleButtonBrowseProjectDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        File file;
        if (! tfProjectDir.getText().isEmpty()) {
            file = new File(tfProjectDir.getText());
            if (! file.isDirectory()) {
                file = new File(System.getProperty("user.home"));
            }
            dirChooser.setInitialDirectory(file);
        }
        Stage stage = (Stage) paneOpenProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfProjectDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonCancelAction(ActionEvent event) {
        System.out.println("OpenProjectController: Cancel");
        closeStage(event);
    }

    @FXML
    private void handleButtonApplyAction(ActionEvent event) {
        System.out.println("OpenProjectController: Apply");
        projectDir.setValue(tfProjectDir.getText());
        closeStage(event);
    }
    
    
    private void closeStage(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
}
