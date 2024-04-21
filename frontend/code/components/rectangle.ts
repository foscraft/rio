import { Color, ComponentId, Fill } from '../dataModels';
import { colorToCssString, fillToCssString } from '../cssUtils';
import { ComponentBase, ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { SingleContainer } from './singleContainer';
import { LayoutContext } from '../layouting';

export type RectangleState = ComponentState & {
    _type_: 'Rectangle-builtin';
    content?: ComponentId | null;
    transition_time?: number;
    cursor?: string;
    ripple?: boolean;

    fill?: Fill;
    stroke_color?: Color;
    stroke_width?: number;
    corner_radius?: [number, number, number, number];
    shadow_color?: Color;
    shadow_radius?: number;
    shadow_offset_x?: number;
    shadow_offset_y?: number;

    hover_fill?: Fill | null;
    hover_stroke_color?: Color | null;
    hover_stroke_width?: number | null;
    hover_corner_radius?: [number, number, number, number] | null;
    hover_shadow_color?: Color | null;
    hover_shadow_radius?: number | null;
    hover_shadow_offset_x?: number | null;
    hover_shadow_offset_y?: number | null;
};

function numberToRem(num: number): string {
    return `${num}rem`;
}

const JS_TO_CSS_VALUE = {
    fill: fillToCssString,
    stroke_color: colorToCssString,
    stroke_width: numberToRem,
    corner_radius: (radii: [number, number, number, number]) =>
        radii.map((num) => `${num}rem`).join(' '),
    shadow_color: colorToCssString,
    shadow_radius: numberToRem,
    shadow_offset_x: numberToRem,
    shadow_offset_y: numberToRem,
};

export class RectangleComponent extends SingleContainer {
    state: Required<RectangleState>;

    // If this rectangle has a ripple effect, this is the ripple instance.
    // `null` otherwise.
    private mdcRipple: MDCRipple | null = null;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-rectangle');
        return element;
    }

    updateElement(
        deltaState: RectangleState,
        latentComponents: Set<ComponentBase>
    ): void {
        let element = this.element;

        this.replaceOnlyChild(latentComponents, deltaState.content);

        if (deltaState.transition_time !== undefined) {
            element.style.transitionDuration = `${deltaState.transition_time}s`;
        }

        if (deltaState.cursor !== undefined) {
            if (deltaState.cursor === 'default') {
                element.style.removeProperty('cursor');
            } else {
                element.style.cursor = deltaState.cursor;
            }
        }

        if (deltaState.ripple === true) {
            if (this.mdcRipple === null) {
                this.mdcRipple = new MDCRipple(element);

                element.classList.add('mdc-ripple-surface');
                element.classList.add('rio-rectangle-ripple');
            }
        } else if (deltaState.ripple === false) {
            if (this.mdcRipple !== null) {
                this.mdcRipple.destroy();
                this.mdcRipple = null;

                element.classList.remove('mdc-ripple-surface');
                element.classList.remove('rio-rectangle-ripple');
            }
        }

        // Apply all the styling properties
        for (let [attrName, js_to_css] of Object.entries(JS_TO_CSS_VALUE)) {
            let value = deltaState[attrName];
            if (value !== undefined) {
                element.style.setProperty(
                    `--rio-rectangle-${attrName}`,
                    js_to_css(value)
                );
            }

            let hoverValue = deltaState['hover_' + attrName];
            if (hoverValue !== undefined) {
                if (hoverValue === null) {
                    // No hover value? Use the corresponding non-hover value
                    element.style.setProperty(
                        `--rio-rectangle-hover-${attrName}`,
                        `var(--rio-rectangle-${attrName})`
                    );
                } else {
                    element.style.setProperty(
                        `--rio-rectangle-hover-${attrName}`,
                        js_to_css(hoverValue)
                    );
                }
            }
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        super.updateAllocatedHeight(ctx);

        // The ripple effect stores the coordinates of its rectangle. Since
        // rio likes to resize and move around components, the rectangle must be
        // updated appropriately.
        if (this.mdcRipple !== null) {
            requestAnimationFrame(() => {
                if (this.mdcRipple !== null) {
                    this.mdcRipple.layout();
                }
            });
        }
    }
}
