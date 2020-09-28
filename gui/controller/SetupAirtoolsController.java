/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.util.ResourceBundle;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.DialogPane;
import javafx.scene.control.TextField;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class SetupAirtoolsController implements Initializable {

    @FXML
    private TextField tfProjectDir;
    @FXML
    private Button buttonBrowseProjectDir;
    @FXML
    private TextField tfRawDir;
    @FXML
    private Button buttonBrowseRawDir;
    @FXML
    private TextField tfTempDir;
    @FXML
    private Button buttonBrowseTempDir;
    @FXML
    private DialogPane setupAirtoolsDialogPane;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        tfProjectDir.setText(System.getenv("HOME") + "/airtools");
        tfRawDir.setText(System.getenv("HOME") + "/raw");
        //tfTempDir.setText(System.getProperty("java.io.tmpdir"));
        tfTempDir.setText(System.getenv("HOME") + "/tmp");
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
        Stage stage = (Stage) setupAirtoolsDialogPane.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfProjectDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonBrowseRawDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        File file;
        if (! tfRawDir.getText().isEmpty()) {
            file = new File(tfRawDir.getText());
            if (! file.isDirectory()) {
                file = new File(System.getProperty("user.home"));
            }
            dirChooser.setInitialDirectory(file);
        }
        Stage stage = (Stage) setupAirtoolsDialogPane.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfRawDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonBrowseTempDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        File file;
        if (! tfTempDir.getText().isEmpty()) {
            file = new File(tfTempDir.getText());
            if (! file.isDirectory()) {
                file = new File(System.getProperty("user.home"));
            }
            dirChooser.setInitialDirectory(file);
        }
        Stage stage = (Stage) setupAirtoolsDialogPane.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfTempDir.setText(file.getAbsolutePath());
        }
    }

    public String getProjectDir() {
        return tfProjectDir.getText();
    }

    public String getRawDir() {
        return tfRawDir.getText();
    }

    public String getTempDir() {
        return tfTempDir.getText();
    }
}
