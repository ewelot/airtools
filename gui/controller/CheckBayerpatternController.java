
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import javafx.application.Platform;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.Label;
import javafx.scene.control.Slider;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class CheckBayerpatternController implements Initializable {

    @FXML
    private AnchorPane paneCheckBayerpattern;
    @FXML
    private TextField tfRawImage;
    @FXML
    private Button buttonBrowseRawImage;
    @FXML
    private ChoiceBox<CropType> cbCropType;
    @FXML
    private Label labelContrast;
    @FXML
    private Slider slContrast;
    @FXML
    private CheckBox cbFlipImage;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private StringProperty rawDir = new SimpleStringProperty();
    private ShellScript sh;
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "check_bayerpattern";

    private enum CropType {
        CENTER30("center 30%"),
        CENTER50("center 50%"),
        NONE("none (full image)")
        ;
        
        private final String description;

        CropType(String description) {
            this.description = description;
        }

        @Override
        public String toString() {
            return description;
        }
    }

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");

        // add combobox items
        cbCropType.getItems().addAll(CropType.CENTER30, CropType.CENTER50, CropType.NONE);
        cbCropType.getSelectionModel().select(0);

        // hide the slider because it is not implemented yet
        labelContrast.setVisible(false);
        slContrast.setVisible(false);

        // jump to end of file name
        tfRawImage.focusedProperty().addListener((c, oldValue, newValue) -> {
            Platform.runLater(() -> {
                //tfMask.deselect();
                tfRawImage.end();
            });
        });
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir, StringProperty rawDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.sh = sh;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);
        this.rawDir = rawDir;
        
        
        paneCheckBayerpattern.setOnMouseClicked(event -> {
            labelWarning.setText("");
        });
    }

    @FXML
    private void onButtonBrowseRawImage(ActionEvent event) {
        System.out.println("CheckBayerpatternController: onButtonBrowseRawImage()");
        FileChooser fileChooser = new FileChooser();
        String fileName = tfRawImage.getText();
        File pdir = new File(rawDir.getValue());
        
        if (fileName.isEmpty()) {
            fileChooser.setInitialDirectory(pdir);
        } else {
            File f = new File(fileName);
            fileChooser.setInitialDirectory(f.getParentFile());
            fileChooser.setInitialFileName(fileName);
        }
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("FITS images", "*.fits", "*.fts", "*.fit")
        );

        Stage stage = (Stage) paneCheckBayerpattern.getScene().getWindow();
        File selectedFile = fileChooser.showOpenDialog(stage);
        if (selectedFile != null) {
            String fullName = selectedFile.getAbsolutePath();
            if (fullName.startsWith(pdir.getAbsolutePath())) {
                tfRawImage.setText(fullName.substring(rawDir.getValue().length()+1));
            } else {
                tfRawImage.setText(selectedFile.getAbsolutePath());
                tfRawImage.end();
            }
            // load raw image file
        }
    }

    
    private boolean isValidInputs() {
        String msg="";
        // TODO: Check for valid coordinate strings
        // TODO: Check for valid region mask file name
        if (tfRawImage.getText().isBlank()) {
            msg="ERROR: no raw image file selected.";
            labelWarning.setText(msg);
            //logger.log(msg);
            return false;
        }
        return true;
    }

    
    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("CheckBayerpatternController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        if (! isValidInputs()) return;
        CropType cropType=cbCropType.getSelectionModel().getSelectedItem();

        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
        
        // add options
        if (cbFlipImage.isSelected())      aircliCmdArgs.add("-f");
        if (cropType == CropType.CENTER30) aircliCmdArgs.add("-c 30");
        if (cropType == CropType.CENTER50) aircliCmdArgs.add("-c 50");
        if (cropType == CropType.NONE)   aircliCmdArgs.add("-a");

        // add mandatory positional parameters
        aircliCmdArgs.add(tfRawImage.getText());

        // run command
        System.out.println("cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        //logger.log("# cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        aircliCmd.setOpts(aircliCmdOpts.toArray(String[]::new));
        aircliCmd.setArgs(aircliCmdArgs.toArray(String[]::new));
        aircliCmd.run();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
}
