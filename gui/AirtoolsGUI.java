/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui;

import tl.airtoolsgui.controller.MainController;
import tl.airtoolsgui.model.SimpleLogger;
import tl.airtoolsgui.model.ShellScript;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Optional;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.binding.Bindings;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Dialog;
import javafx.scene.control.DialogPane;
import javafx.scene.control.Label;
import javafx.scene.image.Image;
import javafx.scene.layout.Region;
import javafx.stage.Modality;
import javafx.stage.Stage;
import tl.airtoolsgui.controller.NewProjectController;
import tl.airtoolsgui.controller.SetupAirtoolsController;

/**
 *
 * @author lehmann
 */
public class AirtoolsGUI extends Application {
    
    private final String progVersion = "4.2";
    private final String progDate = "2022-07-26";
    private final String confFileName = "airtools.conf";
    private final String scriptFileName = "airtools-cli";
    
    private static String addPath = "";
    private final String shareDir = "/usr/share/airtools";
    private final String appIconName = "airtools.png";
    
    @Override
    public void start(Stage stage) throws Exception {
        int majorVersion;
        String newConfDir;      // abs. path to new config dir
        String oldConfDir;      // abs. path to old config dir
        String appIconFileName;
        boolean isFirstProject;

        majorVersion = getMajorVersion(progVersion);
        newConfDir = System.getenv("HOME") + "/.airtools/" + majorVersion;
        oldConfDir = System.getenv("HOME") + "/.airtools/" + (majorVersion-1);
        appIconFileName = shareDir + "/" + appIconName;
        
        // check for config file from previous airtools version
        File file;
        file = new File(newConfDir + "/" + confFileName);
        if (! file.exists() || file.length() == 0) {
            file = new File(oldConfDir + "/" + confFileName);
            if (! file.exists() || file.length() == 0) {
                setupAirtools(newConfDir + "/" + confFileName);
                isFirstProject = true;
            } else {
                updateConfFile(oldConfDir, newConfDir, majorVersion);
                updateParamFiles(oldConfDir, newConfDir, majorVersion);
                isFirstProject = false;
            }
        } else {
            isFirstProject = false;
        }
        
        SimpleLogger logger = new SimpleLogger();
        ShellScript sh = new ShellScript();
        if (! addPath.isEmpty()) System.out.println("addPath=" + addPath);
        sh.setFileName(scriptFileName);
        sh.setAddPath(addPath);
        sh.setLog(logger);
        
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/Main.fxml"));
        Parent root = loader.load();
        
        Scene scene = new Scene(root);
        
        final MainController controller = loader.getController();
        controller.setReferences(newConfDir + "/" + confFileName, sh, logger, progVersion, progDate);
        
        stage.setScene(scene);
        
        // Setting window title
        StringProperty projectDay = new SimpleStringProperty();        
        projectDay.bind(Bindings.createStringBinding(() -> {
            String pDir = controller.getProjectDir().getValue();
            int start=pDir.lastIndexOf("/") + 1;
            return pDir.substring(start);
        }, controller.getProjectDir()));
        stage.titleProperty().bind(Bindings.concat("AIRTOOLS - ").concat(projectDay));
        
        // Application icon
        stage.getIcons().add(new Image("file:" + appIconFileName));

        stage.setOnHidden(e -> Platform.exit());
        stage.setResizable(true);
        stage.getScene().getRoot().getChildrenUnmodifiable().stream().forEach(node -> {
            ((Region)node).setMinWidth(Region.USE_PREF_SIZE);
            ((Region)node).setMinHeight(Region.USE_PREF_SIZE);
        });
        stage.show();
        stage.setMinWidth(stage.getWidth());
        stage.setMinHeight(stage.getHeight());
        //stage.setMaxWidth(1000);
        //stage.setMaxHeight(1000);

        if (isFirstProject) {
            // open "New Project" dialog
            Platform.runLater(() -> {
                controller.showNewProjectDialog();
            });
        }
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        int i=0;
        String arg;
        while (i < args.length && args[i].startsWith("-")) {
            arg = args[i++];

            if (arg.equals("-p")) {
                if (i < args.length) {
                    addPath = args[i++];
                } else {
                    System.err.println("-p requires a path argument");
                    System.exit(255);
                }
            }
            
            if (arg.equals("-a")) {
                System.out.println("# using antialias font settings: prism.text=t2k prism.lcdtext=false");
                System.setProperty("prism.text", "t2k");
                System.setProperty("prism.lcdtext", "false");
            }
        }

        launch(args);
    }

    private int getMajorVersion (String version) {
        int pos = version.indexOf(".");
        return pos >= 0 ? Integer.parseInt(version.substring(0, pos)) : Integer.parseInt(version);
    }
    
    private void setupAirtools(String confFileName) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/SetupAirtools.fxml"));
            DialogPane pane = (DialogPane) loader.load();
            SetupAirtoolsController controller = loader.getController();

            // create dialog
            Dialog dialog = new Dialog();
            dialog.setDialogPane((DialogPane) pane);
            dialog.setTitle("Setup Airtools");
            dialog.initModality(Modality.WINDOW_MODAL);
            //dialog.initOwner(pane.getScene().getWindow());

            ((Button) pane.lookupButton(ButtonType.APPLY)).setText("Apply");
            ((Button) pane.lookupButton(ButtonType.CANCEL)).setText("Cancel");


            Optional<ButtonType> result = dialog.showAndWait();
            if (result.isPresent() && result.get() == ButtonType.APPLY) {
                System.out.println("Creating config file: " + confFileName);
                // create base directories, if necessary
                File dir;
                dir = new File(controller.getProjectDir());
                if (! dir.exists()) dir.mkdirs();
                dir = new File(controller.getRawDir());
                if (! dir.exists()) dir.mkdirs();
                dir = new File(controller.getTempDir());
                if (! dir.exists()) dir.mkdirs();

                // initialize config directory and create config file
                File confFile = new File(confFileName);
                File confDir = new File(confFile.getParent());
                confDir.mkdirs();
                confFile.createNewFile();
                Properties prop = new Properties();
                prop.setProperty("lastProjectDir", controller.getProjectDir());
                prop.setProperty("lastRawDir", controller.getRawDir());
                prop.setProperty("lastTempDir", controller.getTempDir());
                OutputStream outputStream = new FileOutputStream(confFileName);
                prop.store(outputStream, "global settings");
                outputStream.close();

                // copy parameter files from template directory
                String[] parameterFileNames = {"camera.dat", "sites.dat", "refcat.dat"};
                String sourceFileName;
                String targetFileName;
                for (String fileName : parameterFileNames) {
                    sourceFileName = shareDir + "/" + fileName;
                    targetFileName = confDir.getAbsolutePath() + "/" + fileName;
                    if (! new File(targetFileName).exists()) {
                        if (new File(sourceFileName).exists()) {
                            try {
                                Files.copy(Path.of(sourceFileName), Path.of(targetFileName), StandardCopyOption.COPY_ATTRIBUTES);
                            } catch (IOException ex) {
                                System.out.println("ERROR: unable to copy " + fileName);
                                Logger.getLogger(NewProjectController.class.getName()).log(Level.SEVERE, null, ex);
                            }
                        } else {
                            
                        }
                    }
                }
            } else {
                System.exit(1);
            }
        } catch (IOException ex) {
            Logger.getLogger(AirtoolsGUI.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    private void updateConfFile (String oldConfDir, String newConfDir, int newMajorVersion) {
        // convert old config file to match new major program version
        Path source = Path.of(oldConfDir + "/" + confFileName);
        Path target = Path.of(newConfDir + "/" + confFileName);
        /* read initial project settings from config file */
        Properties oldProp = new Properties();
        Properties newProp = new Properties();
        try {
            InputStream inputStream = new FileInputStream(oldConfDir + "/" + confFileName);
            oldProp.load(inputStream);
            inputStream.close();
            if (newMajorVersion == 4) {
                newProp.setProperty("lastProjectDir", oldProp.getProperty("lastProjectDir"));
                newProp.setProperty("lastRawDir", oldProp.getProperty("lastRawDir"));
                newProp.setProperty("lastTempDir", oldProp.getProperty("lastTempDir"));
                newProp.setProperty("lastTZOff", oldProp.getProperty("lastTZOff"));
                newProp.setProperty("lastSite", oldProp.getProperty("lastSite"));
            }
            new File(newConfDir).mkdirs();
            OutputStream outputStream = new FileOutputStream(newConfDir + "/" + confFileName);
            newProp.store(outputStream, "global settings");
            outputStream.close();
        } catch (IOException ex) {
            Logger.getLogger(AirtoolsGUI.class.getName()).log(Level.SEVERE, null, ex);
        }
    };
    
    private void updateParamFiles (String oldConfDir, String newConfDir, int newMajorVersion) {
        Path source;
        Path target;
        String changedParamFiles = "";
        
        // refcat.dat is copied from /usr/share/airtools
        // sites.dat and camera.dat are copied from last config dir if present else from /usr/share/airtools
        for (String paramFileName : new String[]{"camera.dat", "sites.dat", "refcat.dat"}) {
            source = Path.of(oldConfDir + "/" + paramFileName);
            target = Path.of(newConfDir + "/" + paramFileName);
            try {
                if (source.toFile().exists()) {
                    // copy param file from oldConfDir to nemConfDir
                    Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.COPY_ATTRIBUTES);
                } else {
                    Properties oldProp = new Properties();
                    InputStream inputStream = new FileInputStream(oldConfDir + "/" + confFileName);
                    oldProp.load(inputStream);
                    inputStream.close();
                    if (oldProp.getProperty("lastParamDir") != null && !paramFileName.equals("refcat.dat")) {
                        // copy from old lastParamDir to newConfDir
                        source = Path.of(oldProp.getProperty("lastParamDir") + "/" + paramFileName);
                        Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.COPY_ATTRIBUTES);
                        if (! changedParamFiles.isEmpty()) changedParamFiles += ", ";
                        changedParamFiles += paramFileName;
                    } else {
                        // copy template from shareDir
                        source = Path.of(shareDir + "/" + paramFileName);
                        Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.COPY_ATTRIBUTES);
                    }
                }
            } catch (IOException ex) {
                Logger.getLogger(AirtoolsGUI.class.getName()).log(Level.SEVERE, null, ex);
            }
        }

        /* alert the user to check release notes for any required changes of parameter files */
        if (! changedParamFiles.isEmpty()) {
            Label info = new Label(
                    "Please check the release notes about required changes of the\n"
                    + "parameter file(s) " + changedParamFiles + ".\n"
                    + "If this is the case you must edit them before you start any\n"
                    + "image reduction (choose action from menu \"Edit\").\n\n"
            );
            //info.setFont(new Font(14));
            Alert alert = new Alert(Alert.AlertType.WARNING);
            alert.setTitle("Warning");
            alert.setHeaderText("Parameter files were copied from an older AIRTOOLS version.\n");
            alert.getDialogPane().setContent(info);
            alert.showAndWait();
        }
    };
}
