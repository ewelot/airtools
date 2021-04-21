/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.HBox;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class ArchiveController implements Initializable {

    @FXML
    private AnchorPane paneArchive;
    @FXML
    private ChoiceBox<ArchiveType> cbArchiveType;
    @FXML
    private TextField tfImageSets;
    @FXML
    private CheckBox cbDoCopy;
    @FXML
    private HBox hboxCopyDestination;
    @FXML
    private TextField tfDestinationDir;
    @FXML
    private Button buttonBrowseDestinationDir;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "AIarchive";

    
    private enum ArchiveType {
        BASE("Basic Data Only"),
        WCS("Basic + Astrometry Data"),
        RESULTS("Most Results (excluding stacks)"),
        FULL("All Project Data and Images");

        private final String label;

        ArchiveType(String label) {
            this.label = label;
        }

        @Override
        public String toString() {
            return label;
        }
    }

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // fill combo boxes
        cbArchiveType.getItems().setAll(ArchiveType.values());
        cbArchiveType.getSelectionModel().selectFirst();
        
        cbDoCopy.setSelected(false);
        hboxCopyDestination.setDisable(true);
        cbDoCopy.selectedProperty().addListener((observable, oldValue, newValue) -> {
            if (newValue) {
                hboxCopyDestination.setDisable(false);
            } else {
                hboxCopyDestination.setDisable(true);
            }
        });
    }    
    
    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);
        tfDestinationDir.setText(projectDir.getValue() + ".copy");
        labelWarning.setText("");
    }
    
    private boolean isWritableDir (String dirName) {
        /* TODO: check if directory is writable */
        return true;
    }

    private boolean isValidInputs() {
        String msg="";
        if (cbDoCopy.isSelected()) {
            String destDirName = tfDestinationDir.getText();
            if (destDirName.isBlank()) {
                msg="ERROR: destination dir is empty";
            } else if (! isWritableDir(destDirName)) {
                msg="ERROR: destination dir is not writable";
            }
        }
        labelWarning.setText(msg);
        //logger.log(msg);
        return msg.isEmpty();
    }
    
    
    @FXML
    private void onButtonBrowseDestinationDir(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfDestinationDir.getText();
        File f;
        
        if (dirName.isEmpty()) {
            f = new File(projectDir.getValue());
            dirName=f.getParent();
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    f = new File(projectDir.getValue());
                    dirName=f.getParent();
                    file = new File(dirName);
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneArchive.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfDestinationDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("ArchiveController: onButtonStart()");
        labelWarning.setText("");
        List<String> cmdOpts = new ArrayList<>();
        List<String> cmdArgs = new ArrayList<>();

        ArchiveType archiveType=cbArchiveType.getSelectionModel().getSelectedItem();
        if (! isValidInputs()) return;
        
        // add options (airCLITask only)

        // airfun function to call
        cmdArgs.add(airfunFunc);
        

        // add parameters
        if (cbDoCopy.isSelected()) {
            cmdArgs.add("-c " + tfDestinationDir.getText());
        }
        cmdArgs.add("-" + archiveType.name().toLowerCase());
        if (! tfImageSets.getText().isBlank()) {
            cmdArgs.add("\"" + tfImageSets.getText() + "\"");
        }
        
        // run command
        System.out.println("cmd: " + cmdOpts + " " + aircliTask + " " + cmdArgs);
        logger.log("# cmd: " + cmdOpts + " " + aircliTask + " " + cmdArgs);
        aircliCmd.setOpts(cmdOpts.toArray(new String[0]));
        aircliCmd.setArgs(cmdArgs.toArray(new String[0]));
        aircliCmd.run();
        //paneArchive.getScene().getWindow().hide();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }

}
