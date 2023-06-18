/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.BufferedReader;
import tl.airtoolsgui.model.SimpleLogger;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.beans.property.IntegerProperty;
import javafx.beans.property.SimpleIntegerProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import javafx.util.StringConverter;
import tl.airtoolsgui.model.Observer;
import tl.airtoolsgui.model.SitesList;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class NewProjectController implements Initializable {

    @FXML
    private AnchorPane paneNewProject;
    @FXML
    private DatePicker dpDay;
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
    private ComboBox<String> cbSite;
    @FXML
    private Spinner<Integer> spinnerTZOffset;

    @FXML
    private TextField tfObsName;
    @FXML
    private TextField tfObsAddress;
    @FXML
    private TextField tfObsEmail;
    @FXML
    private TextField tfObsIcqID;

    @FXML
    private Label tfErrorMsg;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private StringProperty rawDir = new SimpleStringProperty();
    private StringProperty tempDir = new SimpleStringProperty();
    private StringProperty site = new SimpleStringProperty();
    private IntegerProperty tzoff = new SimpleIntegerProperty();
    private Observer observer;
    
    private final List<String> siteList = new ArrayList<>();
    private final File distDir = new File("/usr/share/airtools");
    private String airtoolsConfDir;
    private final DateTimeFormatter dateFormatter = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd");
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // use custom format with all DatePickers
        dpDay.setConverter(new StringConverter<LocalDate>() {
            @Override 
            public String toString(LocalDate date) {
                if (date != null) {
                    return dateFormatter.format(date);
                } else {
                    return "";
                }
            }

            @Override 
            public LocalDate fromString(String string) {
                if (string != null && !string.isEmpty()) {
                    return LocalDate.parse(string, dateFormatter);
                } else {
                    return null;
                }
            }
        });
        dpDay.setValue(LocalDateTime.now().minusHours(22).toLocalDate());
    }    
    
    
    public void setReferences (String airtoolsConfFileName, SimpleLogger logger, StringProperty projectDir, StringProperty rawDir,
            StringProperty tempDir, StringProperty site, IntegerProperty  tzoff, Observer observer) {
        this.airtoolsConfDir = new File(new File(airtoolsConfFileName).getParent()).getAbsolutePath();
        this.logger=logger;
        this.projectDir=projectDir;
        this.rawDir=rawDir;
        this.tempDir=tempDir;
        this.site=site;
        this.tzoff=tzoff;
        this.observer=observer;
        
        tfErrorMsg.setText("");
        tfProjectDir.setText(projectDir.getValue());
        tfRawDir.setText(rawDir.getValue());
        tfTempDir.setText(tempDir.getValue());
        tfObsName.setText(observer.getName());
        tfObsAddress.setText(observer.getAddress());
        tfObsEmail.setText(observer.getEmail());
        tfObsIcqID.setText(observer.getIcqID());
        handleDpDayAction(null);
        
        // TODO: initialize spinnerTZOffset
        
        populateChoiceBoxSite();
        cbSite.getSelectionModel().selectFirst();
        spinnerTZOffset.setValueFactory(
            new SpinnerValueFactory.IntegerSpinnerValueFactory(-11, 12));
        spinnerTZOffset.getValueFactory().setValue(tzoff.getValue());
    }


    private void populateChoiceBoxSite () {
        System.out.println("populateChoiceBoxSite()");
        cbSite.getItems().clear();
        if (site!=null) {
            cbSite.getItems().add(site.getValue());
        }
        
        File inFile = null;
        try {
            inFile = new File (airtoolsConfDir + "/sites.dat");
            if (inFile.exists()) {
                System.out.println("Info: " + airtoolsConfDir + "/sites.dat found");
            } else {
                inFile = new File (distDir.getPath() + "/sites.dat");
                if (inFile.exists()) {
                    System.out.println("Info: " + distDir.getPath() + "/sites.dat found");
                } else {
                    logger.log("WARNING: file " + distDir.getPath() + "/sites.dat is missing.");
                    return;
                }
            }
            
            SitesList sitesList = new SitesList (inFile, logger);
            if (sitesList.isEmpty()) {
                System.out.println("WARNING: no valid sites found");
                logger.log("WARNING: no valid sites found");
            } else {
                for (String siteName : sitesList.getSiteNames()) {
                    System.out.println("valid site: " + siteName);
                    if (! siteName.equals(site.getValue())) cbSite.getItems().add(siteName);
                }
            }
        } catch (Exception ex) {
            Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
        }
        
    }
    
    
    private void setDayDir(TextField tf, String day) {
        String path;
        File f = new File(tf.getText());
        if (f.getName().matches("[0-9][0-9][0-9][0-9][0-9][0-9].*")) {
            path=f.getParent();
            if (path.equals("/") || path.equals("/home")) path=f.getPath();
        } else {
            path=f.getPath();
        }
        tf.setText(path + "/" + day);
    }
    
    
    @FXML
    private void handleDpDayAction(ActionEvent event) {
        String day;
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyMMdd");
        day = dpDay.getValue().format(fmt);
        System.out.println("day=" + day);
        
        setDayDir(tfProjectDir, day);
        setDayDir(tfRawDir, day);
        setDayDir(tfTempDir, day);
    }

    
    @FXML
    private void handleButtonBrowseProjectDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfProjectDir.getText();
        if (dirName.isEmpty()) {
            dirName=System.getProperty("user.home");
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    file = new File(System.getProperty("user.home"));
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneNewProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfProjectDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonBrowseRawDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfRawDir.getText();
        if (dirName.isEmpty()) {
            dirName=System.getProperty("user.home");
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    file = new File(System.getProperty("user.home"));
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneNewProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfRawDir.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleButtonBrowseTempDirAction(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfTempDir.getText();
        if (dirName.isEmpty()) {
            dirName=System.getProperty("user.home");
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    file = new File(System.getProperty("user.home"));
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneNewProject.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check for file .airtoolsrc, if missing show a warning message
            tfTempDir.setText(file.getAbsolutePath());
        }
    }

    
    private boolean hasFormError () {
        // check for new project directory
        File pDir = new File(tfProjectDir.getText());
        String rcFileName = tfProjectDir.getText() + "/.airtoolsrc";
        File rcFile = new File(rcFileName);
        if (pDir.exists() && rcFile.exists()) {
            tfErrorMsg.setText("ERROR: project directory already exists");
            return true;
        }
        
        // check for site entry
        if (cbSite.getSelectionModel().getSelectedItem().isBlank()) {
            tfErrorMsg.setText("ERROR: the site entry is missing");
            return true;
        }
        
        // no errors found
        tfErrorMsg.setText("");
        return false;
    }
    
    
    @FXML
    private void handleButtonApplyAction(ActionEvent event) {
        System.out.println("NewProjectController: Apply");
        //showUnderConstructionDialog();
        
        String rcFileName = tfProjectDir.getText() + "/.airtoolsrc";
        File rcFile = new File(rcFileName);
        FileWriter fileWriter = null;
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyMMdd");
        String day = dpDay.getValue().format(fmt);

        if (hasFormError()) {
            return;
        }
        
        try {
            // create project directory
            File newDir = new File(tfProjectDir.getText());
            if (newDir.exists()) {
                if (rcFile.exists()) {
                    System.out.println("rcFile = " + rcFile.getAbsolutePath());
                    tfErrorMsg.setText("ERROR: the project directory already exists");
                    return;
                }
            } else {
                if (! newDir.mkdirs()) {
                    tfErrorMsg.setText("ERROR: cannot create the project directory");
                    return;
                }
            }
            // create temp directory
            newDir = new File(tfTempDir.getText());
            if (newDir.exists()) {
                System.out.println("WARNING: the temp directory already exists");
            } else {
                if (! newDir.mkdirs()) {
                    tfErrorMsg.setText("ERROR: cannot create the temp directory");
                    return;
                }
            }
            // check raw directory
            newDir = new File(tfRawDir.getText());
            if (! newDir.exists()) System.out.println("WARNING: raw files directory does not yet exist");

            // create .airtoolsrc
            fileWriter = new FileWriter(rcFileName);
            PrintWriter printWriter = new PrintWriter(fileWriter);
            // mandatory settings
            printWriter.printf("export day=%s\n", day);
            printWriter.printf("export AI_RAWDIR=%s\n", tfRawDir.getText());
            printWriter.printf("export AI_TMPDIR=%s\n", tfTempDir.getText());
            printWriter.printf("export AI_SITE=%s\n", cbSite.getSelectionModel().getSelectedItem());
            printWriter.printf("export AI_TZOFF=%s\n", spinnerTZOffset.getValue());
            // optional settings
            if (tfObsName.getText().isBlank()) {
                printWriter.printf("export AI_OBSNAME=\"%s\"\n", "");
            } else {
                printWriter.printf("export AI_OBSNAME=\"%s\"\n", tfObsName.getText());
            }
            if (tfObsAddress.getText().isBlank()) {
                printWriter.printf("export AI_OBSADDRESS=\"%s\"\n", "");
            } else {
                printWriter.printf("export AI_OBSADDRESS=\"%s\"\n", tfObsAddress.getText());
            }
            if (tfObsEmail.getText().isBlank()) {
                printWriter.printf("export AI_OBSEMAIL=\"%s\"\n", "");
            } else {
                printWriter.printf("export AI_OBSEMAIL=\"%s\"\n", tfObsEmail.getText());
            }
            if (tfObsIcqID.getText().isBlank()) {
                printWriter.printf("export AI_OBSICQID=\"%s\"\n", "OBSxx");
            } else {
                printWriter.printf("export AI_OBSICQID=\"%s\"\n", tfObsIcqID.getText());
            }
            // placeholder for empty settings
            printWriter.printf("export AI_EXCLUDE=\"\"\n");
            printWriter.close();

            // update StringProperties
            rawDir.setValue(tfRawDir.getText());
            tempDir.setValue(tfTempDir.getText());
            site.setValue(cbSite.getSelectionModel().getSelectedItem());
            tzoff.setValue(spinnerTZOffset.getValue());
            // update observer
            observer.setName(tfObsName.getText());
            observer.setAddress(tfObsAddress.getText());
            observer.setEmail(tfObsEmail.getText());
            observer.setIcqID(tfObsIcqID.getText());
            
            // copy parameter files into project directory
            String[] parameterFileNames = {"camera.dat", "sites.dat", "refcat.dat"};
            Path oldPath = null;
            Path newPath = null;
            Path distPath = null;
            File oldFile = null;
            File newFile = null;
            File distFile = null;
            for (String fileName : parameterFileNames) {
                oldPath=Paths.get(airtoolsConfDir + "/" + fileName);
                newPath=Paths.get(tfProjectDir.getText() + "/" + fileName);
                oldFile=new File(oldPath.toString());
                newFile=new File(newPath.toString());
                if (! newFile.exists()) {
                    if (oldFile.exists() && oldFile.isFile()) {
                        try {
                            Files.copy(oldPath, newPath, StandardCopyOption.COPY_ATTRIBUTES);
                        } catch (IOException ex) {
                            logger.log("ERROR: unable to copy " + fileName);
                            Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
                        }
                    } else {
                        if (distDir.exists() && distDir.isDirectory()) {
                            distPath=Paths.get(distDir.getPath() + "/" + fileName);
                            distFile=new File(distPath.toString());
                            if (distFile.exists() && distFile.isFile()) {
                                try {
                                    Files.copy(distPath, newPath, StandardCopyOption.COPY_ATTRIBUTES);
                                } catch (IOException ex) {
                                    logger.log("ERROR: unable to copy " + fileName + " (from DISTDIR)");
                                    Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
                                }
                            } else {
                                logger.log("WARNING: missing " + distPath.toString());
                            }
                        } else {
                            logger.log("WARNING: missing " + oldPath.toString());
                        }
                    }
                } else {
                    logger.log("WARNING: not overwriting file " + newPath.toString());
                }
            }
            
            // note: projectDir must be changed last, because it triggers saveProperties
            projectDir.setValue(tfProjectDir.getText());

            closeStage(event);
        } catch (IOException ex) {
            Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                fileWriter.close();
            } catch (IOException ex) {
                Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    
    private void closeStage(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
    
    private void showUnderConstructionDialog() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Information");
        alert.setHeaderText("Sorry, ...");
        alert.setContentText("this action has not been implemented yet.");
        alert.setResizable(true);
        // TODO: increase size relative to system size
        //alert.getDialogPane().setStyle("-fx-font-size: 14px;");
        //alert.getDialogPane().getScene().getWindow().sizeToScene();
        alert.getDialogPane().setMinHeight(200);
        alert.showAndWait();
    }

    @FXML
    private void handleButtonCancelAction(ActionEvent event) {
        closeStage(event);
    }
}
