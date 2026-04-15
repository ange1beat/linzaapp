import React from "react";

import { PencilToLine, Plus } from "@gravity-ui/icons";
import { Icon, Loader, Modal } from "@gravity-ui/uikit";
import cn from "classnames";
import Cropper, { Area } from "react-easy-crop";
import { useTranslation } from "react-i18next";

import { Button, Text } from "@/shared/ui";

import getCroppedImg from "./getCroppedImg";

import styles from "./Avatar.module.scss";

interface IAvatar {
  avatar?: string | null;
  className?: string;
  onChange: (avatar: Blob) => void;
  isLoad?: boolean;
  disabled?: boolean;
  error?: string;
  defaultAva: string;
}

function Avatar({
  avatar,
  isLoad,
  disabled,
  error,
  onChange,
  className,
  defaultAva,
}: IAvatar) {
  const { t } = useTranslation(["shared.avatar", "controls"]);
  const classes = cn(styles["final-avatar"], className);
  const [crop, setCrop] = React.useState({ x: 0, y: 0 });
  const [zoom, setZoom] = React.useState(1);
  const [srcImage, setSrcImage] = React.useState("");
  const [isCropOpen, setCropOpen] = React.useState(false);

  const [croppedAreaImg, setCroppedAreaImg] = React.useState<Area>({
    width: 0,
    height: 0,
    x: 0,
    y: 0,
  });

  const inputFileRef = React.useRef<HTMLInputElement>(null);
  const onCropComplete = (croppedArea: Area, croppedAreaPixels: Area) => {
    setCroppedAreaImg(croppedAreaPixels);
  };

  const clearInput = () => {
    if (inputFileRef.current) {
      inputFileRef.current.value = "";
    }
  };

  const clearForm = () => {
    clearInput();
    setSrcImage("");
    setCropOpen(false);
    setCrop({ x: 0, y: 0 });
    setZoom(1);
  };

  const onSaveAvatar = async () => {
    clearForm();
    const croppedImage = await getCroppedImg(srcImage, croppedAreaImg);
    if (croppedImage) {
      setSrcImage("");
      onChange(croppedImage);
    }
  };
  const onChangeImage = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target && event.target.files) {
      setSrcImage(URL.createObjectURL(event.target.files[0]));
      setCropOpen(true);
    }
  };
  return (
    <div className={classes}>
      <Modal open={isCropOpen} onClose={() => {}}>
        <div className={styles["crop-image"]}>
          <div className={styles["crop-image__cropper"]}>
            <Cropper
              image={srcImage}
              crop={crop}
              zoom={zoom}
              aspect={1}
              onCropChange={setCrop}
              cropShape="round"
              showGrid={false}
              onZoomChange={setZoom}
              onCropComplete={onCropComplete}
            />
          </div>
          <div className={styles["crop-image__button-wrapper"]}>
            <Button size="l" onClick={clearForm} view="normal">
              {t("cancel", { ns: "controls" })}
            </Button>
            <Button view="action" size="l" onClick={onSaveAvatar}>
              {t("apply", { ns: "controls" })}
            </Button>
          </div>
        </div>
      </Modal>
      <input
        className={styles["input-load-file"]}
        ref={inputFileRef}
        type="file"
        onChange={onChangeImage}
      />
      <div className={classes}>
        {isLoad ? (
          <Loader className={styles["finale-avatar__loader"]} size="s" />
        ) : (
          <img
            className={styles["final-avatar__img"]}
            src={avatar || defaultAva}
            alt="user avatar"
          />
        )}
        <Button
          className={styles["final-avatar__buttons"]}
          view="normal"
          size="m"
          disabled={disabled}
          iconLeft={
            avatar ? <Icon data={PencilToLine} /> : <Icon data={Plus} />
          }
          onClick={() => inputFileRef.current?.click()}
        >
          {avatar ? t("change") : t("add")}
        </Button>

        {error && (
          <Text variant="body-2" className={styles["final-avatar__error"]}>
            {t(`${error}`)}
          </Text>
        )}
      </div>
    </div>
  );
}

export default Avatar;
