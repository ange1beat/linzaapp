import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Accordion from "./index";

describe("Accordion", () => {
  it("Default view", () => {
    const tree = render(
      <Accordion>
        <Accordion.Head>Header</Accordion.Head>
        <Accordion.Body>
          Folder long name to check how is it will be display in my component
          <input placeholder="some content" />
          <button>Button!</button>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. A, aliquid
            commodi eos fugiat ipsam minima molestias nam omnis quam recusandae
            repellat, vero! Dicta dolorum illum nulla quae qui quisquam rem!
            Animi deleniti eligendi id natus ut? Asperiores cumque debitis
            distinctio esse est eveniet ex inventore maxime neque nesciunt
            nostrum omnis, perferendis perspiciatis quia, quidem saepe sapiente
            sint, sit temporibus voluptatum? Aliquam ea eos ex iste nemo nihil
            odio odit sunt? Culpa eaque earum error eum fuga hic provident quam
            quisquam sed. Consequatur fuga iste laudantium molestiae odio
            quisquam, ullam veniam.
          </p>
        </Accordion.Body>
      </Accordion>,
    );
    expect(tree).toMatchSnapshot();
  });
});
