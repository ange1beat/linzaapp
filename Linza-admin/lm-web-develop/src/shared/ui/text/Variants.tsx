import Text from "./index";

import styles from "./Variants.module.scss";

function Variants() {
  return (
    <div className={styles["storybook-text-wrapper"]}>
      <h1>Variants</h1>
      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Body</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Body-1</h3>
          <Text variant="body-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>

        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Body-2</h3>
          <Text variant="body-2">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Body-3</h3>
          <Text variant="body-3">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Body-short</h3>
          <Text variant="body-short">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Caption</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Caption-1</h3>
          <Text variant="caption-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Caption-2</h3>
          <Text variant="caption-2">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Header</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Header-1</h3>
          <Text variant="header-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Header-2</h3>
          <Text variant="header-2">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Subheader</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Subheader-1</h3>
          <Text variant="subheader-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <Text variant="subheader-2">
            <h3>Subheader-2</h3>
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Subheader-3</h3>
          <Text variant="subheader-3">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Display</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Display-1</h3>
          <Text variant="display-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Display-2</h3>
          <Text variant="display-2">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Display-3</h3>
          <Text variant="display-3">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Display-4</h3>
          <Text variant="display-4">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Code</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Code-1</h3>
          <Text variant="code-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Code-2</h3>
          <Text variant="code-2">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Code-3</h3>
          <Text variant="code-3">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Code inline</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Code-inline-1</h3>
          <Text variant="code-inline-1">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Code-inline-2</h3>
          <Text variant="code-inline-2">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Code-inline-3</h3>
          <Text variant="code-inline-3">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>

      <div className={styles["storybook-text-wrapper__variants"]}>
        <h2>Custom variants</h2>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Modal-name</h3>
          <Text variant="modal-name">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
        <div className={styles["storybook-text-wrapper__variants"]}>
          <h3>Modal-email</h3>
          <Text variant="modal-email">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis
            culpa enim facilis iure nobis odio reprehenderit suscipit totam. Ab
            odit quidem ullam? Accusamus culpa eum quae quis sed sequi veniam.
          </Text>
        </div>
      </div>
    </div>
  );
}

export default Variants;
